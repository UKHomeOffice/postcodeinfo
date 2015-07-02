# -*- coding: utf-8 -*-
import os
from os.path import dirname, join

import tempfile
import unittest

import django

from postcode_api.models import Address
from postcode_api.importers.addressbase_basic_importer import \
    AddressBaseBasicImporter
from postcode_api.importers.addressbase_basic_importer import batch, csv_rows



class AddressBaseBasicImporterTest(django.test.TestCase):

    def setUp(self):
        self.importer = AddressBaseBasicImporter()
        self.sample_data = join(
            dirname(__file__),
            '../sample_data/addressbase_basic_sample.csv')

    def test_import(self):
        self.importer.import_csv(self.sample_data)
        self.assertEqual(5, Address.objects.count())

    # def test_updates_no_duplicates(self):
    #     self.test_import()
    #     self.test_import()

    # def test_imported_address_has_correct_attributes(self):
    #     self.test_import()

    #     address = Address.objects.filter(uprn='100040311658').first()
    #     self.assertEqual('EX6 8BP', address.postcode)
    #     self.assertEqual('ex68bp', address.postcode_index)
    #     self.assertEqual('ex6', address.postcode_area)
    #     self.assertEqual(25, address.building_number)
    #     self.assertEqual('osgb1000002274402191', address.os_address_toid)
    #     self.assertEqual('JUPES CLOSE', address.thoroughfare_name)
    #     self.assertEqual('EXMINSTER', address.dependent_locality)
    #     self.assertEqual(
    #         '25 Jupes Close\nExminster\nExeter\nEX6 8BP',
    #         address.formatted_address)
    #     lon, lat = address.point.coords
    #     self.assertAlmostEqual(50.6762502757, lat)
    #     self.assertAlmostEqual(-3.49205126583, lon)
