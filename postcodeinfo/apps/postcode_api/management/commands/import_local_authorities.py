import os

from multiprocessing import Pool
from django.core.management.base import BaseCommand, CommandError

from postcode_api.importers.local_authorities_importer \
    import LocalAuthoritiesImporter


class Command(BaseCommand):
    args = '<csv_file csv_file...>'

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError(
                'You must specify at least one csv file - '
                'you might want to download one from, for example, '
                'https://geoportal.statistics.gov.uk/geoportal/'
                'rest/find/document?searchText='
                'Local%20Authority%20Districts%20UK&f=pjson')

        p = Pool()
        p.map(import_local_authorities, args)


def import_local_authorities(filename):
    if not os.access(filename, os.R_OK):
        raise CommandError('.nt file ' + filename + ' could not be read')

    importer = LocalAuthoritiesImporter()
    importer.import_local_authorities(filename)
