import csv
import re
from typing import Dict, List, Union
from collections import OrderedDict

from django.core.management import BaseCommand

from crm.models import Line, ReelManufacturer, ReelModel, SpoolModel, SpoolDimension, ReducerModel, ReducerDimension


class Command(BaseCommand):
    ARG_NAME = "file_path"

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument(self.ARG_NAME, nargs='+', type=str)
        parser.add_argument(self.ARG_NAME, type=str)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     help='Delete poll instead of closing it',
        # )

    def handle(self, *args, **options):
        file_path = options.get(self.ARG_NAME)

        if file_path:
            with open(file_path) as csvfile:
                reader = csv.DictReader(csvfile)

                current_model = None
                current_line = None
                for record in reader:
                    if self._record_empty(record):
                        continue

                    if not record.get('model'):
                        record['model'] = current_model
                    else:
                        current_model = record['model']

                    if not record.get('line'):
                        record['line'] = current_line
                    else:
                        current_line = record.get("line")

                    self._handle_record(record)

    def _record_empty(self, record: dict):
        return not list(filter(None, record.values()))

    def _handle_record(self, record: OrderedDict):
        line = record.get("line")
        line_obj = self._get_line(line)

        model_obj = self._get_model(record.get("model"))

        assert model_obj

        spool_obj = self._get_spool(model_obj, record)

        assert spool_obj

        self._create_spool_dim(spool_obj, record)

        reducer_obj = self._get_reducer_model(spool_obj, line_obj)

        assert reducer_obj

        self._create_reducer_dim(reducer_obj, record)

    def _create_reducer_dim(self, reducer_model: ReducerModel, record: Dict[str, str]):
        for d3, d4, h2 in self._unpack_dim(record.get("d3"), record.get("d4"), record.get("h2")):
            dim_obj, created = ReducerDimension.objects.get_or_create(
                reducer_model=reducer_model,
                D3=self._valid_float(d3),
                D4=self._valid_float(d4),
                H2=self._valid_float(h2),
                description=record.get("description"))

    def _get_reducer_model(self, spool_model: SpoolModel, line: Line):
        reducer_obj, created = ReducerModel.objects.get_or_create(
            spool_model=spool_model,
            line=line)
        return reducer_obj

    def _create_spool_dim(self, spool_model: SpoolModel, record: Dict[str, str]):

        for d1, d2, h1 in self._unpack_dim(record.get("d1"), record.get("d2"), record.get("h1")):
            dim_obj, created = SpoolDimension.objects.get_or_create(
                spool_model=spool_model,
                D1=self._valid_float(d1),
                D2=self._valid_float(d2),
                H1=self._valid_float(h1))

    def _unpack_dim(self, d1, d2, h, last_val: list = [None, None, None]):
        cur_d1, cur_d2, cur_h = last_val
        for dim in self._zip_lists(d1.split("/"), d2.split("/"), h.split("/")):
            if not next(filter(None, dim), None):
                continue
            d1, d2, h = dim
            if not d1:
                if cur_d1:
                    d1 = cur_d1
                else:
                    continue

            if not d2:
                if cur_d2:
                    d2 = cur_d2
                else:
                    continue

            if not h:
                if cur_h:
                    h = cur_h
                else:
                    continue
            yield d1, d2, h
            last_val[0] = d1
            last_val[1] = d2
            last_val[2] = h

    def _zip_lists(self, *args):
        max_len = len(max(*args, key=len))
        eq_it = map(lambda v: v + [v[-1]] * (max_len - len(v)), args)
        return zip(*eq_it)

    def _valid_float(self, value: Union[str, float]) -> float:
        if isinstance(value, float):
            return value
        return float(value.replace(",", "."))

    def _get_spool(self, model_obj: ReelModel, record: dict):
        spool_name = " ".join(record.get("model").strip().split("_")[2:])
        size = re.search(r"([\d]{4,})", spool_name)
        if size:
            size = size.group(1)

        spool_obj, created = SpoolModel.objects.get_or_create(
            name=spool_name.strip().capitalize(),
            reel_model=model_obj,
            size=size)
        return spool_obj

    def _get_model(self, model: str):
        model_list = model.strip().split("_")
        if len(model_list) < 2:
            return
        manufacturer, model = model_list[0:2]
        man_obj, created = ReelManufacturer.objects.get_or_create(
            name=str(manufacturer).strip().capitalize())
        model_obj, created = ReelModel.objects.get_or_create(
            name=str(model).strip().capitalize(),
            reel_manufacturer=man_obj)
        return model_obj

    def _get_line(self, line: str):
        # diameter, length = line.strip().split('-')
        line_list = line.strip().split('-')
        if len(line_list) < 2:
            line_list.append("0")
        diameter, length = line_list
        if "," in length or "." in length:
            length, diameter = diameter, length
        p, created = Line.objects.get_or_create(
            length=int(length),
            diameter=float(diameter.replace(",", ".")))
        return p
