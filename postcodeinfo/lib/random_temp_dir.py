# -*- encoding: utf-8 -*-
import os, random, string, tempfile

class RandomTempDir(object):
  def __init__(self, *args, **kwargs):
    self.root = kwargs.pop('root', '/tmp/')
    self.dirname = self.random_string(kwargs.pop('length', 8))
    self.full_path = os.path.join(self.root, self.dirname)

  def temp_dir(self, prefix="test_filesystem_cache"):
      return tempfile.mkdtemp(prefix=prefix)

  def random_string(self, length):
      return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

  def temp_file_path(self):
      return os.path.join(self.dirname, self.random_string(8))
