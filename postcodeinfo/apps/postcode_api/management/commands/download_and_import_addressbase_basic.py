import os
import re
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from StringIO import StringIO

import zipfile
from zipfile import ZipFile

from postcode_api.downloaders.addressbase_basic_downloader import AddressBaseBasicDownloader
from postcode_api.importers.addressbase_basic_importer import AddressBaseBasicImporter

class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir', 
                action='store_true', 
                dest='destination_dir',
                default='/tmp/addressbase_basic/')

        # Named (optional) arguments
        parser.add_argument('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force download even if previous download exists')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
          os.makedirs(options['destination_dir'])

        downloaded_file = self.__download(options['destination_dir'], options.get('force', False) )
        if downloaded_file:
            return self.__process(downloaded_file)
        else:
            print 'nothing downloaded - nothing to import'
            return None

    def __download(self, destination_dir, force=False):
        print 'downloading'
        downloader = AddressBaseBasicDownloader()
        return downloader.download(destination_dir, force)

    def __process(self, filepath):
        files = self.__unzip_if_needed(filepath)

        for path in files:
            print 'importing ' + path
            self.__import(path)
            self.__cleanup(path)

        if file.exists(filepath):
            self.__cleanup(filepath)

        return True

    def __unzip_if_needed(self, filepath):
        if zipfile.is_zipfile(filepath):
            print 'unzipping'
            return self.__unzip(filepath)
        else:
            return [filepath]


    def __unzip(self, zipfile_path):
        extracted_files = []
        dirname = os.path.dirname(zipfile_path)
        thezip = ZipFile(zipfile_path, 'r')
        
        for info in thezip.infolist():
            if re.match( '.*AddressBase_.*\.csv', info.filename ):
                extracted_path = thezip.extract(info, dirname)
                extracted_files.append( extracted_path )
                print 'extracted ' + extracted_path
            else:
                print 'ignored ' + info.filename

        return extracted_files

    def __import(self, downloaded_file):
        importer = AddressBaseBasicImporter()
        importer.import_addressbase_basic(downloaded_file)

    def __cleanup(self, downloaded_file):
        print 'removing local file ' + downloaded_file
        os.remove(downloaded_file)
