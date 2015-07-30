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
                    country, created = Country.objects.get_or_create(gss_code=row['CTRY14CD'])
                    country.name = row['CTRY14NM']
                    country.save()
