from django.test import TestCase

from postcode_api.models import Address
from postcode_api.utils import AddressFormatter


class AddressFormatterTestCase(TestCase):
    pass


cases = {

    'test_simple_address': {
        'address': Address(
            building_number=16,
            thoroughfare_name='VIXEN ROAD',
            post_town='BRADDOCK',
            postcode='KT6 5BT'),
        'formatted':
            u'16 Vixen Road\nBraddock\nKT6 5BT'},

    'test_first_last_building_name_chars_numeric': {
        'address': Address(
            building_name='1-2',
            thoroughfare_name='NURSERY LANE',
            dependent_locality='PENN',
            post_town='HIGH WYCOMBE',
            postcode='HP10 8LS'),
        'formatted':
            u'1-2 Nursery Lane\nPenn\nHigh Wycombe\nHP10 8LS'},

    'test_first_penultimate_building_name_chars_numeric_last_alpha': {
        'address': Address(
            building_name='12A',
            thoroughfare_name='UPPERKIRKGATE',
            post_town='ABERDEEN',
            postcode='AB10 1BA'),
        'formatted':
            u'12A Upperkirkgate\nAberdeen\nAB10 1BA'},

    'test_one_char_building_name': {
        'address': Address(
            building_name='K',
            thoroughfare_name='PORTLAND ROAD',
            post_town='DORKING',
            postcode='RH4 1EW'),
        'formatted':
            u'K, Portland Road\nDorking\nRH4 1EW'},

    'test_organisation_name': {
        'address': Address(
            organisation_name='LEDA ENGINEERING LTD',
            dependent_locality='APPLEFORD',
            post_town='ABINGDON',
            postcode='OX14 4PG'),
        'formatted':
            u'Leda Engineering Ltd\nAppleford\nAbingdon\nOX14 4PG'},

    'test_building_name_exception_with_dependent_thoroughfare': {
        'address': Address(
            building_name='1A',
            dependent_thoroughfare_name='SEASTONE COURT',
            thoroughfare_name='STATION ROAD',
            post_town='HOLT',
            postcode='NR25 7HG'),
        'formatted':
            u'1A Seastone Court\nStation Road\nHolt\nNR25 7HG'},

    'test_building_name_only': {
        'address': Address(
            building_name='THE MANOR',
            thoroughfare_name='UPPER HILL',
            post_town='HORLEY',
            postcode='RH6 0HP'),
        'formatted':
            u'The Manor\nUpper Hill\nHorley\nRH6 0HP'},

    'test_building_name_only_ends_with_simple_number': {
        'address': Address(
            organisation_name='JAMES VILLA HOLIDAYS',
            building_name='CENTRE 30',
            thoroughfare_name='ST. LAURENCE AVENUE',
            post_town='GRAFTON',
            postcode='ME16 0LP'),
        'formatted':
            u'James Villa Holidays\nCentre 30\n'
            'St. Laurence Avenue\nGrafton\nME16 0LP'},

    'test_building_name_and_building_number': {
        'address': Address(
            building_name='VICTORIA HOUSE',
            building_number=15,
            thoroughfare_name='THE STREET',
            post_town='CHRISTCHURCH',
            postcode='BH23 6AA'),
        'formatted':
            u'Victoria House\n15 The Street\nChristchurch\nBH23 6AA'},

    'test_sub_building_name_and_building_number': {
        'address': Address(
            sub_building_name='FLAT 1',
            building_number=12,
            thoroughfare_name='LIME TREE AVENUE',
            post_town='BRISTOL',
            postcode='BS8 4AB'),
        'formatted':
            u'Flat 1\n12 Lime Tree Avenue\nBristol\nBS8 4AB'},

    # PAF docs table 28B
    # no addresses in the current PAF seem to require this formatting
    # 'test_sub_building_name_and_building_name': {
    #     'address': Address(
    #         sub_building_name='A',
    #         building_number=12,
    #         thoroughfare_name='HIGH STREET NORTH',
    #         dependent_locality='COOMBE BISSETT',
    #         post_town='SALISBURY',
    #         postcode='SP5 4NA'),
    #     'formatted':
    #         u'12A High Street North\nCoombe Bissett\nSalisbury\nSP5 4NA'},

    'test_numeric_sub_building_name_and_building_name_and_building_number_exception': {
        'address': Address(
            sub_building_name='10B',
            building_name='BARRY JACKSON TOWER',
            thoroughfare_name='ESTONE WALK',
            post_town='BIRMINGHAM',
            postcode='B6 5BA'),
        'formatted':
            u'10B Barry Jackson Tower\nEstone Walk\nBirmingham\nB6 5BA'},

    'test_numeric_sub_building_name_and_building_name_and_building_number': {
        'address': Address(
            sub_building_name='STABLES FLAT',
            building_name='THE MANOR',
            thoroughfare_name='UPPER HILL',
            post_town='HORLEY',
            postcode='RH6 0HP'),
        'formatted':
            u'Stables Flat\nThe Manor\nUpper Hill\nHorley\nRH6 0HP'},

    'test_alpha_sub_building_name_and_building_name_and_building_number_exception': {
        'address': Address(
            sub_building_name='2B',
            building_name='THE TOWER',
            building_number=27,
            thoroughfare_name='JOHN STREET',
            post_town='WINCHESTER',
            postcode='SO23 9AP'),
        'formatted':
            u'2B The Tower\n27 John Street\nWinchester\nSO23 9AP'},

    'test_alpha_sub_building_name_and_building_name_and_building_number': {
        'address': Address(
            sub_building_name='BASEMENT FLAT',
            building_name='VICTORIA HOUSE',
            building_number=15,
            thoroughfare_name='THE STREET',
            post_town='CORYTON',
            postcode='BP23 6AA'),
        'formatted':
            u'Basement Flat\nVictoria House\n15 The Street\nCoryton\nBP23 6AA'}
}


def make_test(case):
    address = case['address']
    formatted = case['formatted']

    def case_test(self):
        self.assertEqual(formatted, AddressFormatter.format(address))

    return case_test


for name, case in cases.iteritems():
    setattr(AddressFormatterTestCase, name, make_test(case))
