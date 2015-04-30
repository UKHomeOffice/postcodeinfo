import os
from django.core.management.base import BaseCommand, CommandError

from postcode_api.downloaders.local_authorities_downloader import LocalAuthoritiesDownloader

class Command(BaseCommand):
    args = '<destination_dir>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]

        downloader = LocalAuthoritiesDownloader()
        downloaded_file = downloader.download(destination_dir)
        print 'returning ' + str(downloaded_file)
        return downloaded_file
