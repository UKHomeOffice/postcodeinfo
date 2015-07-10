import os
from django.core.management.base import BaseCommand

from postcode_api.downloaders import LocalAuthoritiesDownloader
from postcode_api.importers.local_authorities_importer \
    import LocalAuthoritiesImporter
from postcode_api.utils import ZipExtractor


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
            self._process(downloaded_files)
        else:
            print 'nothing downloaded - nothing to import'

    def _download(self, destination_dir):
        print 'downloading'
        downloader = LocalAuthoritiesDownloader()
        return downloader.download(destination_dir)

    def _process(self, filepath):
        if isinstance(filepath, list):
            filepath = filepath[0]
        files = ZipExtractor(filepath).unzip_if_needed('.*\.nt')

        for path in files:
            print 'importing ' + path
            self._import(path)

    def _import(self, downloaded_file):
        importer = LocalAuthoritiesImporter()
        importer.import_local_authorities(downloaded_file)
