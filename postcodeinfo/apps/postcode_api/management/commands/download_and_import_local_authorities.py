import os
from django.core.management.base import BaseCommand

from postcode_api.downloaders import LocalAuthoritiesDownloader
from postcode_api.importers.local_authorities_importer \
    import LocalAuthoritiesImporter
from postcode_api.utils import flatten


class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir',
                            action='store_true',
                            dest='destination_dir',
                            default='/tmp/local_authorities/')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
            os.makedirs(options['destination_dir'])

        downloaded_files = self._download(options['destination_dir'])
        if downloaded_files:
            for path in flatten([downloaded_files]):
                self._import(path)
        else:
            print 'nothing downloaded - nothing to import'

    def _download(self, destination_dir):
        print 'downloading'
        downloader = LocalAuthoritiesDownloader()
        return downloader.download(destination_dir)

    def _import(self, downloaded_file):
        print 'importing {file}'.format(file=downloaded_file)
        importer = LocalAuthoritiesImporter()
        importer.import_local_authorities(downloaded_file)
