import os
import re
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from StringIO import StringIO


from postcode_api.utils import ZipExtractor
from postcode_api.downloaders.postcode_gss_code_downloader \
    import PostcodeGssCodeDownloader
from postcode_api.importers.postcode_gss_code_importer \
    import PostcodeGssCodeImporter


def exit_code(key):
    return {'OK': 0, 'GENERIC_ERROR': 1}[key]


class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir',
                            action='store_true',
                            dest='destination_dir',
                            default='/tmp/postcode_gss_codes/')

        # Named (optional) arguments
        parser.add_argument('--force',
                            action='store_true',
                            dest='force',
                            default=False,
                            help='Force download '
                                 'even if previous download exists')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
            os.makedirs(options['destination_dir'])

        downloaded_file = self._download(
            options['destination_dir'], options.get('force', False))
        if downloaded_file:
            self._process(downloaded_file)
            return exit_code('OK')
        else:
            print 'nothing downloaded - nothing to import'
            return exit_code('OK')

    def _download(self, destination_dir, force=False):
        print 'downloading'
        downloader = PostcodeGssCodeDownloader()
        return downloader.download(destination_dir, force)

    def _process(self, filepath):
        files = ZipExtractor(filepath).unzip_if_needed('.*NSPL.*\.csv')
        for path in files:
            print 'importing ' + path
            self._import(path)
            self._cleanup(path)

        if os.path.exists(filepath):
            self._cleanup(filepath)

        return True

    def _import(self, downloaded_file):
        importer = PostcodeGssCodeImporter()
        importer.import_postcode_gss_codes(downloaded_file)

    def _cleanup(self, downloaded_file):
        print 'removing local file ' + downloaded_file
        os.remove(downloaded_file)
