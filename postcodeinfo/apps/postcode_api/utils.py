import logging
import os
import re

import zipfile
from zipfile import ZipFile

from titlecase import titlecase


class AddressFormatter(object):

    """
    Heavily inspired by https://github.com/DanMeakin/getputpostcode
    """
    @classmethod
    def format(cls, address):
        addr = u''

        for k in ['department_name', 'organisation_name', 'po_box_number']:
            v = titlecase(getattr(address, k))
            if v:
                addr += u"%s\n" % v

        addr += cls.format_building(address.sub_building_name,
                                    address.building_name,
                                    address.building_number)

        for k in ['dependent_thoroughfare_name', 'thoroughfare_name',
                  'double_dependent_locality', 'dependent_locality',
                  'post_town', 'postcode']:
            if k == 'postcode':
                addr += u"%s\n" % getattr(address, k)
            elif getattr(address, k):
                addr += u"%s\n" % titlecase(getattr(address, k))

        return '\n'.join(a for a in addr.split('\n') if a)

    @classmethod
    def format_building(cls, sub_name, name, number):
        if not any([sub_name, name, number]):
            return ''

        # Define exception to the usual rule requiring a newline for the
        # building name. See p. 27 of PAF Guide for further information.
        building_str = ''
        exception = re.compile(r"^\d.*\d$|^\d.*\d[A-Za-z]$|^\d[A-Za-z]$|^.$")

        for component in [sub_name, name]:
            if component and exception.match(component):
                building_str += component
                if re.match(r"^[A-Za-z]$", component):
                    building_str += u", "
                else:
                    building_str += u" "
            else:
                # Check if final portion of string is numeric/alphanumeric. If
                # so, split and apply exception to that section only.
                parts = titlecase(component).split(' ')
                final = parts.pop()

                if (exception.match(component) and
                        not number and
                        not re.match(r'/^\d*$/', final)):
                    building_str += u"%s\n%s " % (' '.join(parts), final)
                else:
                    building_str += u"%s\n" % titlecase(component)

        if number:
            building_str += u"%d " % number

        return building_str.lstrip()


class ZipExtractor(object):

    def __init__(self, filepath):
        self.filepath = filepath

    def unzip_if_needed(self, pattern):
        if zipfile.is_zipfile(self.filepath):
            return self.unzip(pattern)
        return [self.filepath]

    def unzip(self, pattern):
        extracted_files = []
        dirname = os.path.dirname(self.filepath)
        thezip = ZipFile(self.filepath, 'r')

        for info in thezip.infolist():
            if re.match(pattern, info.filename):
                extracted_path = thezip.extract(info, dirname)
                extracted_files.append(extracted_path)
                logging.debug('extracted ' + extracted_path)
            else:
                logging.debug('ignored ' + info.filename)

        return extracted_files

# flatten a list in which each element may or may not be a list itself
# from http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


