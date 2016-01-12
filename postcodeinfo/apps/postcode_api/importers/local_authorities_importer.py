import csv
import logging

from django.db import transaction

from postcode_api.models import LocalAuthority
from postcode_api.utils import ZipExtractor


log = logging.getLogger(__name__)


class LocalAuthoritiesImporter(object):

    def __init__(self):
        self.graph = None

    def import_local_authorities(self, filename):
        files = ZipExtractor(filename).unzip_if_needed('.*LAD.*\.csv')
        for path in files:
            print 'importing {path}'.format(path=path)
            self._process(path)

    def _process(self, filename):
        la_count = LocalAuthority.objects.count()
        log.info(
            'Existing LocalAuthority count = {count}'.format(
                count=str(la_count)))

        self._import_csv_file(filename)

        new_count = LocalAuthority.objects.count()
        log.info('{count} local authorities added'.format(
            count=str(new_count - la_count)))
        log.info(
            'There are now {new_count} local authorities'.format(
                new_count=str(new_count)))

    def _import_csv_file(self, filename):
        with open(filename) as f:
            # DictReader will skip the header automatically
            reader = csv.DictReader(f, delimiter=',')

            with transaction.atomic():
                LocalAuthority.objects.all().delete()
                for row in reader:
                    LocalAuthority(
                        gss_code=row['LAD14CD'],
                        name=row['LAD14NM']
                    ).save()
