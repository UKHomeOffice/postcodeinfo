# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import dirname, join

from django.db import migrations

from postcode_api.importers.countries_importer import CountriesImporter


def create_countries(apps, schema_editor):
    data_file = join( dirname(__file__), '../data/countries.csv' )
    CountriesImporter().import_csv(data_file)


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0012_create_country_and_country_gss_code'),
    ]

    operations = [
        migrations.RunPython(create_countries),
    ]
