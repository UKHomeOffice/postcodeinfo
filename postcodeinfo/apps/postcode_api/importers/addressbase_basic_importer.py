import csv
import itertools
import os

from dateutil.parser import parse as parsedate
from django.contrib.gis.geos import Point
from django.db import transaction

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
        collection = {'I': self.inserts,
         'U': self.updates,
         'D': self.deletes}[change_type]

        collection.append(address)

    def import_csv(self, filename):
        total_rows = lines_in_file(filename)
        batch_size = int( os.environ.get( 'BATCH_IMPORT_NUM_ROWS', (total_rows // 10) or 1 ) )
        bulk_create_batch_size = int(os.environ.get('BULK_CREATE_BATCH_SIZE', 1000))

        rows = csv_rows(filename, fieldnames=self.fieldnames)

        print( 'reading all data and getting uprns' )
        print 'getting batches of size {i}'.format(i=batch_size)
        batches = batch(rows, batch_size)
        
        for this_batch in batches:
            batch_list = list(this_batch)
            print '**** starting batch ****'
            uprns = self._get_all_uprns(batch_list)

            # get all existing addresses with a uprn in this batch
            print( 'looking for existing addresses with uprns in this batch' )
            existing_address_dict = self._get_existing_addresses_in_batch_as_dict(uprns)

            print 'constructing model objects'
            self._construct_model_objects( batch_list, existing_address_dict, total_rows)

            print '**** saving ****'
            self._save(bulk_create_batch_size)

            print 'batch done'

    def _get_all_uprns(self, batch_list):
        uprns = []
        for row in batch_list:
            if row:
                uprns.append( row['uprn'] )

        return uprns

    def _get_existing_addresses_in_batch_as_dict(self, uprns):
        print( 'querying db for existing uprns')
        existing_addresses = Address.objects.filter(uprn__in=uprns)
            
        print( 'building hash' )
        return dict ((o.uprn, o) for o in existing_addresses)

    def _construct_model_objects(self, batch_list, existing_address_dict, total_rows):
        with ImporterProgress(total_rows) as progress:
            for row in batch_list:
                if row:
                    address = self._process(row, existing_address_dict)
                    self._append(row['change_type'], address)
                    progress.increment(row['uprn'])
                else:
                    print( 'row empty!' )

    def _save(self, bulk_create_batch_size):
        print 'bulk_create_batch_size = {batch_size}'.format(batch_size=bulk_create_batch_size)

        to_delete = [obj.pk for obj in self.updates + self.deletes]

        with transaction.atomic():
            print 'deleting %i addresses' % len(to_delete)
            Address.objects.filter(pk__in=to_delete).delete()

            # delete inserts which are already in the db and re-insert them
            inserts = [obj.pk for obj in self.inserts]
            print 'deleting {num} existing addresses to insert in batches of {batch_size}'.format(num=len(inserts), batch_size=bulk_create_batch_size)
            Address.objects.filter(pk__in=inserts).delete()

            print 'bulk_creating {num} updates in batches of {batch_size}'.format(num=len(inserts), batch_size=bulk_create_batch_size)
            Address.objects.bulk_create(self.updates, bulk_create_batch_size)

            print 'bulk_creating %i inserts' % len(self.inserts)
            Address.objects.bulk_create(self.inserts, bulk_create_batch_size)

        self.inserts = []
        self.updates = []
        self.deletes = []

    def _process(self, row, existing_address_dict):
        # try/except is faster in Python than testing each key
        try:
            address = existing_address_dict[row['uprn']]
        except KeyError:
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
