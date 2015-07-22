import os
from django.core.management.base import BaseCommand

from postcode_api.downloaders import AddressBaseBasicDownloader
from postcode_api.importers.addressbase_basic_importer \
    import AddressBaseBasicImporter
from postcode_api.utils import ZipExtractor


class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir',
                            action='store_true',
                            dest='destination_dir',
                            default='/tmp/addressbase_basic/')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
            os.makedirs(options['destination_dir'])

        downloaded_files = self._download(options['destination_dir'])
        if downloaded_files:
            self._process_all(downloaded_files)
        else:
            print 'nothing downloaded - nothing to import'

    def _download(self, destination_dir):
        print 'downloading'
        downloader = AddressBaseBasicDownloader()
        return downloader.download(destination_dir)

    def _process_all(self, files):
        if isinstance(files, list):
            files_to_process = []
            for filepath in files:
                extracted_files = ZipExtractor(filepath).unzip_if_needed(
                    '.*AddressBase_.*\.csv')
                files_to_process += extracted_files
            self._import(files_to_process)
        else:
            self._process(files)

    def _process(self, filepath):
        files = ZipExtractor(filepath).unzip_if_needed(
            '.*AddressBase_.*\.csv')

        self._import(files)

    def _import(self, downloaded_files):
        importer = AddressBaseBasicImporter()
        importer.import_csv(downloaded_files)
