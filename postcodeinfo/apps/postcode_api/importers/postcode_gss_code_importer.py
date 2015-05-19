import os
import csv
import time


from dateutil.parser import parse as parsedate
from time import time, gmtime

from postcode_api.models import PostcodeGssCode, Download
from postcode_api.importers.progress_reporter import ProgressReporter


class PostcodeGssCodeImporter(object):

    def __init__(self):
        self.progress = ProgressReporter()

    def import_postcode_gss_codes(self, filename):

        with open(filename, "rb") as csvfile:
            self.progress.start(filename)
            datareader = csv.reader(csvfile)
            # skip the header row!
            datareader.next()
            for row in datareader:
                self.import_row(row)
                self.progress.row_processed(row[0])

            self.progress.finish()

            self.update_download(filename)

    def import_row(self, row):
        postcode = row[0]
        local_authority_gss_code = row[11]
        normalized_postcode = postcode.replace(' ', '').lower()
        mapping = self.find_or_create_lookup(normalized_postcode)
        mapping.local_authority_gss_code = local_authority_gss_code
        mapping.save()

    def find_or_create_lookup(self, postcode_index):
        try:
            a = PostcodeGssCode.objects.get(postcode_index=postcode_index)
        except PostcodeGssCode.DoesNotExist:
            a = PostcodeGssCode(postcode_index=postcode_index)
        return a

    def update_download(self, filename):
        dl = Download.objects.filter(
            local_filepath=filename, state='downloaded').first()
        if dl:
            dl.state = 'imported'
            dl.last_state_change = gmtime()
            dl.save()
