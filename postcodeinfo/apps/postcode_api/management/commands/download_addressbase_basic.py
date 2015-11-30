from django.core.management.base import BaseCommand

from postcode_api.downloaders import AddressBaseBasicDownloader


class Command(BaseCommand):
    args = '<destination_dir>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]
        destination_dir = destination_dir or '/tmp/addressbase_basic'

        downloader = AddressBaseBasicDownloader()
        downloaded_files = downloader.download(destination_dir)
