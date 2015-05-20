import re
import os

from django.test import TestCase

from postcode_api.models import Address
from postcode_api.importers.addressbase_basic_importer import AddressBaseBasicImporter


class AddressBaseBasicImporterTestCase(TestCase):

    def __sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

    def __importer(self):
        return AddressBaseBasicImporter()

    def __import_data_from(self, file):
        self.__importer().import_csv(self.__sample_data_file(file))

    def test_that_address_objects_get_the_right_attributes(self):
        self.__import_data_from('addressbase_basic_sample.csv')
        address = Address.objects.filter(uprn='100040311658').first()
        self.assertEqual(address.postcode, 'EX6 8BP')
        self.assertEqual(address.postcode_index, 'ex68bp')
        self.assertEqual(address.postcode_area, 'ex6')
        self.assertEqual(address.building_number, 25)
        self.assertEqual(address.os_address_toid, 'osgb1000002274402191')
        self.assertEqual(address.thoroughfare_name, 'JUPES CLOSE')
        self.assertEqual(address.dependent_locality, 'EXMINSTER')
        self.assertEqual(
            address.formatted_address, '25 Jupes Close\nExminster\nExeter\nEX6 8BP')
        long_delta = abs(address.point.coords[0] - -3.49205126583)
        lat_delta = abs(address.point.coords[1] - 50.6762502757)
        self.assertEqual((long_delta <= 0.00000001), True)
        self.assertEqual((lat_delta <= 0.00000001), True)

    def test_that_when_new_addresses_are_imported_then_address_records_get_created(self):
        # setup
        self.assertEqual(Address.objects.count(), 0)
        self.__import_data_from('addressbase_basic_sample.csv')
        # expectation
        self.assertEqual(Address.objects.count(), 5)

    def test_that_when_existing_addresses_are_imported_then_duplicate_address_records_dont_get_created(self):
        # setup
        self.__import_data_from('addressbase_basic_sample.csv')
        self.assertEqual(Address.objects.count(), 5)
        self.__import_data_from('addressbase_basic_sample.csv')
        # expectation
        self.assertEqual(Address.objects.count(), 5)
