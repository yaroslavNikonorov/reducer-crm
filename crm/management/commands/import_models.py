import csv
import re
from collections import OrderedDict

from django.core.management import BaseCommand

from crm.models import Line, Manufacturer, Model, SpoolModel


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
        # model = re
        line = record.get("line")
        line_obj = self._get_line(line)

        model_obj = self._get_model(record.get("model"))

        assert model_obj

        spool_obj = self._get_spool(model_obj, record)

        assert spool_obj

    def _get_spool_dim(self, spool_model: SpoolModel, record):
        pass

    def _get_spool(self, model_obj: Model, record: dict):
        spool_name = " ".join(record.get("model").strip().split("_")[2:])
        size = re.search(r"([\d]{4,})", spool_name)
        if size:
            size = size.group(1)

        spool_obj, created = SpoolModel.objects.get_or_create(
            name=spool_name.strip().capitalize(),
            model=model_obj,
            size=size)
        return spool_obj

    def _get_model(self, model: str):
        model_list = model.strip().split("_")
        if len(model_list) < 2:
            return
        manufacturer, model = model_list[0:2]
        man_obj, created = Manufacturer.objects.get_or_create(
            name=str(manufacturer).strip().capitalize())
        model_obj, created = Model.objects.get_or_create(
            name=str(model).strip().capitalize(),
            manufacturer=man_obj)
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
