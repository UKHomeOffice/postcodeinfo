# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations
from django.conf import settings

from postcode_api.downloaders.postcode_gss_code import PostcodeGssCodeDownloader
from postcode_api.importers.postcode_gss_code_importer import PostcodeGssCodeImporter
from postcode_api.utils import ZipExtractor

def rerun_nspl_import(apps, schema_editor):
  if settings.DEBUG or settings.TESTING:
      print 'not in production - skipping re-import of NSPL'
  else:
    destination_dir = dest_dir('/tmp/postcode_gss_codes/')
    filepath = PostcodeGssCodeDownloader().download(destination_dir)
    if isinstance(filepath, list):
        filepath = filepath[0]
        
    files = ZipExtractor(filepath).unzip_if_needed('.*NSPL.*\.csv')
    for path in files:
        print 'importing ' + path
        PostcodeGssCodeImporter().import_postcode_gss_codes(path)


def dest_dir(path):
  if not os.path.exists(path):
    os.makedirs(path)
  return path

class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0013_populate_countries'),
    ]

    operations = [
      migrations.RunPython(rerun_nspl_import)
    ]
