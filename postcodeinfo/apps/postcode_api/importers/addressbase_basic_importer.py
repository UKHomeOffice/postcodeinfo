import csv
import glob
import itertools
import logging
import os
import subprocess

from django.conf import settings


#: EPSG projection code
BRITISH_NATIONAL_GRID = 27700



def split_file(path, num_lines):
    split_dir = os.path.join(os.path.dirname(path), 'splits')
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)

    filename = os.path.basename(path)
    split_file_prefix = os.path.join(split_dir, filename + '-')
    cmd = ["/usr/bin/split", "-l", str(num_lines), path, split_file_prefix]
    runProcess(cmd)
    logging.debug('globbing for ' + split_file_prefix + '*')
    return glob.glob(split_file_prefix + '*')


def get_all_uprns(batch_list):
    return [row['uprn'] for row in batch_list if row]


def runProcess(exe, **kwargs):
    env = kwargs.pop('env', {})
    logging.debug(
        'executing {cmd} with env {env}'.format(cmd=str(exe), env=env))
    p = subprocess.Popen(
        exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    while(True):
        retcode = p.poll()  # returns None while subprocess is running
        line = p.stdout.readline()
        if line:
            print line
        if(retcode is not None):
            break


class AddressBaseBasicImporter(object):

    fields = [
        ("uprn", "char"),
        ("os_address_toid", "char"),
        ("rm_udprn", "char"),
        ("organisation_name", "char"),
        ("department_name", "char"),
        ("po_box_number", "char"),
        ("building_name", "char"),
        ("sub_building_name", "char"),
        ("building_number", "int"),
        ("dependent_thoroughfare_name", "char"),
        ("thoroughfare_name", "char"),
        ("post_town", "char"),
        ("double_dependent_locality", "char"),
        ("dependent_locality", "char"),
        ("postcode", "char"),
        ("postcode_type", "char"),
        ("x_coordinate", "point"),
        ("y_coordinate", "point"),
        ("rpc", "int"),
        ("change_type", "char"),
        ("start_date", "date"),
        ("last_update_date", "date"),
        ("entry_date", "date"),
        ("primary_class", "char"),
        ("process_date", "date"),
    ]

    def _append(self, change_type, address):
        collection = {
            'I': self.inserts,
            'U': self.updates,
            'D': self.deletes}[change_type]

        collection.append(address)

    def import_csv(self, filename):
        logging.debug("importing csv {filename}".format(filename=filename))
        batch_size = int(
            os.environ.get('BATCH_IMPORT_NUM_ROWS', 100000))

        split_files = split_file(filename, batch_size)

        for file_to_import in split_files:
            logging.debug("importing csv {filename}".format(filename=filename))
            self.import_file(file_to_import)
            os.remove(file_to_import)

    def import_file(self, filepath):
        logging.debug("importing file {filepath}".format(filepath=filepath))
        script = os.path.join(
            settings.BASE_DIR, 'scripts/', 'addressbase_import.sh')
        # need to explicitly pass through the DB_NAME as an env var here,
        # because when running tests, Django automatically changes the name in settings to
        # 'test_xyz', but *doesn't* alter the DB_NAME env var - so we have to override it
        # otherwise tests that try to import stuff in setup then read it back, will fail
        env = {'DB_NAME': settings.DATABASES['default']['NAME'],
               'DB_HOST': settings.DATABASES['default']['HOST'],
               'DB_USERNAME': settings.DATABASES['default']['USER'],
               'DB_PASSWORD': settings.DATABASES['default']['PASSWORD']
               }
        runProcess(
            [script, filepath], env=env)
