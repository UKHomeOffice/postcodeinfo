import tempfile
import logging
import os
import subprocess

from django.conf import settings


#: EPSG projection code
BRITISH_NATIONAL_GRID = 27700


def split_file(path, num_lines):
    filename = os.path.basename(path)
    split_dir = tempfile.mkdtemp(prefix=filename + '-')
    split_file_prefix = split_dir + "/"
    runProcess(
        ['/usr/bin/split', '-l', str(num_lines), path, split_file_prefix])

    for filename in os.listdir(split_dir):
        filepath = os.path.join(split_dir, filename)
        yield filepath
        os.remove(filepath)

    os.rmdir(split_dir)


def get_all_uprns(batch_list):
    return [row['uprn'] for row in batch_list if row]


def runProcess(exe, **kwargs):
    env = kwargs.pop('env', {})
    logging.debug(
        'executing {cmd} with env {env}'.format(cmd=str(exe), env=env))
    p = subprocess.Popen(
        exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    p.wait()


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

    def import_all(self, filepaths):
        self.import_file(filepaths)

    def import_csv(self, filename):
        logging.debug("importing csv {filename}".format(filename=filename))
        batch_size = int(
            os.environ.get('BATCH_IMPORT_NUM_ROWS', 100000))

        for split in split_file(filename, batch_size):
            self.import_file(split)

    def import_file(self, filepath):
        logging.debug("importing file {filepath}".format(filepath=filepath))
        script = os.path.join(
            settings.BASE_DIR, 'scripts/', 'addressbase_import.sh')
        # need to explicitly pass through the DB_NAME as an env var here,
        # because when running tests, Django automatically changes the name in settings to
        # 'test_xyz', but *doesn't* alter the DB_NAME env var - so we have to override it
        # otherwise tests that try to import stuff in setup then read it back,
        # will fail
        env = self._db_env()
        runProcess(
            [script, filepath], env=env)

    def _db_env(self):
        return {'DB_NAME': settings.DATABASES['default']['NAME'],
                'DB_HOST': settings.DATABASES['default']['HOST'],
                'DB_USERNAME': settings.DATABASES['default']['USER'],
                'DB_PASSWORD': settings.DATABASES['default']['PASSWORD']
                }
