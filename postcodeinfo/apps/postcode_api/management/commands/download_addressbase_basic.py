from django.core.management.base import BaseCommand, CommandError

from postcode_api.downloaders.addressbase_basic_downloader import AddressBaseBasicDownloader

class Command(BaseCommand):
    args = '<destination_dir>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]

        downloader = AddressBaseBasicDownloader()
        downloaded_file = downloader.download(destination_dir)
        return downloaded_file
