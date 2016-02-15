# -*- coding: utf-8 -*-
from os.path import dirname, join

import django
import time

from django.contrib.gis.geos import Point

from postcode_api.models import Address
from postcode_api.importers.addressbase_basic_importer import \
    AddressBaseBasicImporter

# extends TransactionTestCase and explicitly deletes all addresses
# in setUp because the importer shell script does its own
# manual transaction handling, and the two interfere


class AddressBaseBasicImporterTest(django.test.TransactionTestCase):

    def setUp(self):
        self.importer = AddressBaseBasicImporter()
        self.sample_data = join(
            dirname(__file__),
            '../sample_data/addressbase_basic_sample.csv')

    def tearDown(self):
        Address.objects.all().delete()

    def test_import(self):
        self.importer.import_csv(self.sample_data)
        self.assertEqual(5, Address.objects.count())

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
        self.assertAlmostEqual(56.1277805, lat)
        self.assertAlmostEqual(-3.148169, lon)

    def test_that_running_import_twice_on_same_data_produces_same_result(self):
        self.test_import()
        self.test_import()

    def test_that_running_import_replaces_any_existing_data(self):
        dummy_date = time.strftime("%Y-%m-%d")
        Address.objects.create(postcode_index='abcdef',
                               point=Point(123, 123),
                               rpc=012345,
                               uprn=1234567890,
                               start_date=dummy_date,
                               last_update_date=dummy_date,
                               entry_date=dummy_date,
                               process_date=dummy_date
                               )
        self.test_import()
        self.assertEqual(None, Address.objects.filter(uprn=1234567890).first() )

