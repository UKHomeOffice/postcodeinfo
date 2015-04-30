import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from postcode_api.downloaders.postcode_gss_code_downloader import PostcodeGssCodeDownloader

class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def handle(self, *args, **options):
        destination_dir = '/tmp/postcode_gss_codes/'
        if len(args) == 1:
            destination_dir = args[0]

        if not os.path.exists(destination_dir):
          os.makedirs(destination_dir)

        print 'downloading'
        result = call_command('download_postcode_gss_codes', destination_dir )
        if result:
          print 'result = ' + result
          print 'importing'
          call_command('import_postcode_gss_codes', destination_dir )
          print 'removing local file'
          os.remove('/tmp/postcode_gss_codes/*')

