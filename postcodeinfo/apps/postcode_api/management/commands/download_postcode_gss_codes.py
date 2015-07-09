from django.core.management.base import BaseCommand

from postcode_api.downloaders import PostcodeGssCodeDownloader


class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def handle(self, *args, **options):
        destination_dir = None
        if len(args) == 1:
            destination_dir = args[0]

        downloader = PostcodeGssCodeDownloader()
        downloaded_files = downloader.download(destination_dir)
