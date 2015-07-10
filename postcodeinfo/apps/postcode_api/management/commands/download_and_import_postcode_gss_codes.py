import os
from django.core.management.base import BaseCommand

from postcode_api.utils import ZipExtractor
from postcode_api.downloaders import PostcodeGssCodeDownloader
from postcode_api.importers.postcode_gss_code_importer \
    import PostcodeGssCodeImporter


class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir',
                            action='store_true',
                            dest='destination_dir',
                            default='/tmp/postcode_gss_codes/')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
            os.makedirs(options['destination_dir'])

        downloaded_files = self._download(options['destination_dir'])
        if downloaded_files:
            self._process(downloaded_files)
        else:
            print 'nothing downloaded - nothing to import'

    def _download(self, destination_dir, force=False):
        print 'downloading'
        downloader = PostcodeGssCodeDownloader()
        return downloader.download(destination_dir, force)

    def _process(self, filepath):
        if isinstance(filepath, list):
            filepath = filepath[0]
        files = ZipExtractor(filepath).unzip_if_needed('.*NSPL.*\.csv')
        for path in files:
            print 'importing ' + path
            self._import(path)

        return True

    def _import(self, downloaded_file):
        importer = PostcodeGssCodeImporter()
        importer.import_postcode_gss_codes(downloaded_file)
