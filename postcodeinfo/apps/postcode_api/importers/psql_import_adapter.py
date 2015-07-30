import logging
import os
import subprocess

from django.conf import settings


def runProcess(exe, **kwargs):
    env = kwargs.pop('env', {})
    logging.debug(
        'executing {cmd} with env {env}'.format(cmd=str(exe), env=env))
    p = subprocess.Popen(
        exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    p.wait()


class PSQLImportAdapter(object):

    def import_csv(self, script_name, filepaths):
        logging.debug(
            "importing file(s) {filepaths}".format(filepaths=filepaths))
        script = os.path.join(
            settings.BASE_DIR, 'scripts/', script_name)
        # need to explicitly pass through the DB_NAME as an env var here,
        # because when running tests, Django automatically changes the
        # name in settings to 'test_xyz', but *doesn't* alter the DB_NAME
        # env var - so we have to override it, otherwise tests that try
        # to import stuff in setup then read it back, will fail
        env = self._db_env()
        if not isinstance(filepaths, list):
            filepaths = [filepaths]

        runProcess(
            [script] + filepaths, env=env)

    def _db_env(self):
        return {
            'DB_NAME': settings.DATABASES['default']['NAME'],
            'DB_HOST': settings.DATABASES['default']['HOST'],
            'DB_USERNAME': settings.DATABASES['default']['USER'],
            'DB_PASSWORD': settings.DATABASES['default']['PASSWORD']
        }
