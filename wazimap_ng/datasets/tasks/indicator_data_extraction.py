import json
import logging
from collections import defaultdict

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform

from .. import models
from itertools import groupby

logger = logging.getLogger(__name__)

class DataAccumulator:
    def __init__(self, geography_id, primary_group=None):
        self.geography_id = geography_id
        self.data = {
            "groups": defaultdict(dict),
            "subindicators": {}
        }

        self.primary_group = primary_group

    def add_data(self, group, subindicator, data_blob):
        self.data["groups"][group][subindicator] = data_blob["data"]

    def add_subindicator(self, data_blob):
        subindicators = {}
        data_blob = list(data_blob)
        if len(data_blob) == 0:
            return

        datum_copy = dict(data_blob[0])
        count = datum_copy.pop("count")
        values = list(datum_copy.values())
        if len(values) == 0:
            raise Exception("Missing subindicator in datablob")
        elif len(values) == 1:
            for datum in data_blob:
                count = datum.pop("count")
                values = list(datum.values())
                subindicator = values[0]
                subindicators[subindicator] = count
            self.data["subindicators"] = subindicators
        else:
            for datum in data_blob:
                count = datum.pop("count")
                subindicator = datum.pop(self.primary_group)
                values = list(datum.values())
                group2_subindicator = values[0]

                group_dict = subindicators.setdefault(subindicator, {})
                group_dict[group2_subindicator] = count
            subindicators_arr = []
            for group_subindicator, values in subindicators.items():
                subindicators_arr.append({
                    "group": group_subindicator,
                    "values": values
                })

            self.data["subindicators"] = subindicators_arr


    @property
    def subindicators(self):
        return self.data["subindicators"]

class Sorter:
    def __init__(self, primary_group=None):
        self.accumulators = {}
        self.primary_group = primary_group

    def get_accumulator(self, geography_id):
        if geography_id not in self.accumulators:
            self.accumulators[geography_id] = DataAccumulator(geography_id, self.primary_group)

        accumulator = self.accumulators[geography_id]
        return accumulator

    def add_data(self, group, subindicator, data_blob):
        for datum in data_blob:
            geography_id = datum["geography_id"]
            accumulator = self.get_accumulator(geography_id)

            accumulator.add_data(group, subindicator, datum)

    def add_subindicator(self, data_blob):
        for datum in data_blob:
            geography_id = datum["geography_id"]
            accumulator = self.get_accumulator(geography_id)
            accumulator.add_subindicator(datum["data"])


@transaction.atomic
def indicator_data_extraction(indicator, **kwargs):
    sorter = Sorter()

    models.IndicatorData.objects.filter(indicator=indicator).delete()

    for group in indicator.dataset.group_set.all():
        logger.debug(f"Extracting subindicators for: {group.name}")
        qs = models.DatasetData.objects.filter(dataset=indicator.dataset, data__has_keys=[group.name])
        if group.name != indicator.primary_group:
            subindicators = qs.get_unique_subindicators(group.name)

            for subindicator in subindicators:
                logger.debug(f"Extracting subindicators for: {group.name} -> {subindicator}")
                qs_subindicator = qs.filter(**{f"data__{group.name}": subindicator})

                counts = extract_counts(indicator, qs_subindicator)
                sorter.add_data(group.name, subindicator, counts)
        else:
            counts = extract_counts(indicator, qs)
            sorter.add_subindicator(counts)


    datarows = []
    for geography_id, accumulator in sorter.accumulators.items():
        datarows.append(models.IndicatorData(
            indicator=indicator, geography_id=geography_id, data=accumulator.data
        )
    )

    models.IndicatorData.objects.bulk_create(datarows, 1000)

    return {
        "model": "indicator",
        "name": indicator.name,
        "id": indicator.id,
    }           

def extract_counts(indicator, qs):
    """
    Data extraction for indicator data object.

    Create Indicator data object for indicator object and all geography.

    This task populates the Json field in indicator data object.

    Data json field should be populated with json of group name in groups of indicator
    and total count of that group according to geography.

    So for Gender group object should look like : {"Gender": "Male", "count": 123, ...}
    """

    if indicator.universe is not None:
        qs = qs.filter_by_universe(indicator.universe)

    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("count", "data"), FloatField())

    qs = qs.exclude(data__count="")
    qs = qs.order_by("geography_id")
    data = groupby(qs.grouped_totals_by_geography(groups), lambda x: x["geography_id"])

    datarows = []
    for geography_id, group in data:
        data_dump = json.dumps(list(group))
        grouped = json.loads(data_dump.replace("data__", ""))

        for item in grouped:
            item.pop("geography_id")

        datarows.append({"geography_id": geography_id, "data": grouped})
    return datarows
