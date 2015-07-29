import csv
import logging

from postcode_api.models import Country


class CountriesImporter(object):

    def import_csv(self, *filepaths):
        for data_file in filepaths:
            logging.debug('importing {data_file}'.format(data_file=data_file))
            with open(data_file) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    country = self.find_or_create_country(row['CTRY14CD'])
                    country.name = row['CTRY14NM']
                    country.save()

    def find_or_create_country(self, gss_code):
        try:
            c = Country.objects.get(gss_code=gss_code)
        except Country.DoesNotExist:
            c = Country(gss_code=gss_code)
        return c
