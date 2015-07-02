# -*- coding: utf-8 -*-
from os.path import dirname, join


import django

from postcode_api.models import Address
from postcode_api.importers.addressbase_basic_importer import \
    AddressBaseBasicImporter

# extends TransactionTestCase and explicitly deletes all addresses
# in setUp because the importer shell script does its own 
# manual transaction handling, and the two interfere
class AddressBaseBasicImporterTest(django.test.TransactionTestCase):

    def setUp(self):
        Address.objects.all().delete()
        self.importer = AddressBaseBasicImporter()
        self.sample_data = join(
            dirname(__file__),
            '../sample_data/addressbase_basic_sample.csv')

    def test_import(self):
        self.importer.import_csv(self.sample_data)
        self.assertEqual(5, Address.objects.count())

    def test_updates_no_duplicates(self):
        self.test_import()
        self.test_import()

    def test_imported_address_has_correct_attributes(self):
        self.test_import()

        address = Address.objects.filter(uprn='320012010').first()
        self.assertEqual('KY1 2HS', address.postcode)
        self.assertEqual('ky12hs', address.postcode_index)
        self.assertEqual('ky1', address.postcode_area)
        self.assertEqual(50, address.building_number)
        self.assertEqual('osgb1000002280373585', address.os_address_toid)
        self.assertEqual('BEATTY CRESCENT', address.thoroughfare_name)
        self.assertEqual('KIRKCALDY', address.post_town)
        self.assertEqual(
            '50 Beatty Crescent\nKirkcaldy\nKY1 2HS',
            address.formatted_address)
        lon, lat = address.point.coords
        self.assertAlmostEqual(56.1277867963, lat)
        self.assertAlmostEqual(-3.1481671533, lon)
