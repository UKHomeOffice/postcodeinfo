from django.core.management.base import BaseCommand

from postcode_api.downloaders import LocalAuthoritiesDownloader


class Command(BaseCommand):
    args = '<destination_dir>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]

        downloader = LocalAuthoritiesDownloader()
        downloaded_files = downloader.download(destination_dir)
