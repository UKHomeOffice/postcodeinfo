import os
from django.core.management.base import BaseCommand, CommandError

from postcode_api.downloaders.postcode_gss_code_downloader import PostcodeGssCodeDownloader

class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]

        downloader = PostcodeGssCodeDownloader()
        downloaded_file = downloader.download(destination_dir)
        return downloaded_file
