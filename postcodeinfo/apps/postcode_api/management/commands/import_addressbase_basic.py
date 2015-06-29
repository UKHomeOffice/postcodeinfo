import os

from multiprocessing import Pool
from django.core.management.base import BaseCommand, CommandError

from postcode_api.importers.addressbase_basic_importer \
    import AddressBaseBasicImporter


class Command(BaseCommand):
    args = '<csv_file csv_file...>'

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('You must specify at least one CSV file')

        # p = Pool()
        # p.map(import_csv, args)
        for i in range(len(args)):
            import_csv(args[i])


def import_csv(filename):
    if not os.access(filename, os.R_OK):
        raise CommandError('CSV file could not be read')

    importer = AddressBaseBasicImporter()
    importer.import_csv(filename)
