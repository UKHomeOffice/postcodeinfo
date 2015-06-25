import csv
import itertools

from dateutil.parser import parse as parsedate
from django.contrib.gis.geos import Point

from postcode_api.models import Address
from postcode_api.importers.progress_reporter import ImporterProgress, \
    lines_in_file


#: EPSG projection code
BRITISH_NATIONAL_GRID = 27700


def unicode_csv_reader(utf8_data, fieldnames=None, **kwargs):
    csv_reader = csv.DictReader(utf8_data, fieldnames=fieldnames, **kwargs)
    for row in csv_reader:
        yield {key: unicode(cell, 'utf-8') for key, cell in row.items()}


def csv_rows(filename, fieldnames=None, **kw):
    with open(filename, 'rb') as csv_file:
        for row in unicode_csv_reader(csv_file, fieldnames=fieldnames, **kw):
            yield row


def batch(iterable, size):
    "batch([1,2,3,4,5,6,7], 3) => [[1,2,3],[4,5,6],[7]]"
    it = iter(iterable)
    while True:
        chunk = itertools.islice(it, size)
        yield itertools.chain((next(chunk),), chunk)


class AddressBaseBasicImporter(object):

    fields = [
        ("uprn", "char"),
        ("os_address_toid", "char"),
        ("rm_udprn", "char"),
        ("organisation_name", "char"),
        ("department_name", "char"),
        ("po_box_number", "char"),
        ("building_name", "char"),
        ("sub_building_name", "char"),
        ("building_number", "int"),
        ("dependent_thoroughfare_name", "char"),
        ("thoroughfare_name", "char"),
        ("post_town", "char"),
        ("double_dependent_locality", "char"),
        ("dependent_locality", "char"),
        ("postcode", "char"),
        ("postcode_type", "char"),
        ("x_coordinate", "point"),
        ("y_coordinate", "point"),
        ("rpc", "int"),
        ("change_type", "char"),
        ("start_date", "date"),
        ("last_update_date", "date"),
        ("entry_date", "date"),
        ("primary_class", "char"),
        ("process_date", "date"),
    ]

    def __init__(self):
        self.inserts = []
        self.updates = []
        self.deletes = []
        self.fieldnames = map(lambda (k, _): k, self.fields)

    def _append(self, change_type, address):
        {'I': self.inserts,
         'U': self.updates,
         'D': self.deletes}[change_type].append(address)

    def import_csv(self, filename):
        total_rows = lines_in_file(filename)
        batch_size = (total_rows // 50) or 1
        with ImporterProgress(total_rows) as progress:
            rows = csv_rows(filename, fieldnames=self.fieldnames)
            for rows in batch(rows, batch_size):
                for row in rows:
                    if row:
                        address = self._process(row)
                        self._append(row['change_type'], address)
                        progress.increment(row['uprn'])
                self._save()

    def _save(self):
        to_delete = [obj.pk for obj in self.updates + self.deletes]
        Address.objects.filter(pk__in=to_delete).delete()

        # delete inserts which are already in the db and re-insert them
        inserts = [obj.pk for obj in self.inserts]
        Address.objects.filter(pk__in=inserts).delete()

        Address.objects.bulk_create(self.updates)
        Address.objects.bulk_create(self.inserts)

        self.inserts = []
        self.updates = []
        self.deletes = []

    def _process(self, row):
        try:
            address = Address.objects.get(uprn=row['uprn'])
        except Address.DoesNotExist:
            address = Address(uprn=row['uprn'])

        for i, (field, data_type) in enumerate(self.fields):
            if data_type == 'char':
                setattr(address, field, row[field])
            if data_type == 'int' and row[field] != '':
                setattr(address, field, int(row[field]))
            if data_type == 'date' and row[field] != '':
                setattr(address, field, parsedate(row[field]))

        address.postcode_index = row['postcode'].replace(' ', '').lower()

        address.point = Point(
            float(row['x_coordinate']),
            float(row['y_coordinate']),
            srid=BRITISH_NATIONAL_GRID
        )

        return address
