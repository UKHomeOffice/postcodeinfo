import mock, shutil, unittest

from postcode_api.caches.filesystem_cache import FilesystemCache
from random_temp_dir import RandomTempDir



class FilesystemCacheTest(unittest.TestCase):
   
    def setUp(self):
        self.root_dir = RandomTempDir()
        self.temp_file_path = self.root_dir.temp_file_path()
        self.cache = FilesystemCache(self.root_dir.full_path)

    def tearDown(self):
        shutil.rmtree(self.root_dir.full_path, True)
        

    def test_that_when_the_given_key_exists_then_get_copies_the_file_to_filename(self):
        self.cache.has = mock.MagicMock(return_value=False)
        with mock.patch( 'shutil.copy2', return_value='copied' ) as mock_copy:
            FilesystemCache().get('my_key', self.root_dir.full_path)
            mock_copy.assert_called_with_arguments(self.root_dir.full_path)


    def test_that_when_the_given_key_does_not_exist_then_get_does_not_copy_the_file(self):
        self.cache.has = mock.MagicMock(return_value=False)
        with mock.patch( 'shutil.copy2' ) as mock_copy:
            FilesystemCache().get('my_key', self.root_dir.full_path)
            self.assertEqual(False, mock_copy.called)

    def test_that_when_the_given_key_exists_then_has_returns_true(self):
        with mock.patch( 'os.path.isfile', return_value=True ):
            self.assertEqual(True, FilesystemCache().has('some key'))

    def test_that_when_the_given_key_does_not_exist_then_has_returns_false(self):
        with mock.patch( 'os.path.isfile', return_value=False ):
            self.assertEqual(False, FilesystemCache().has('some key'))

    def test_that_put_sets_the_given_cache_key_with_the_contents_of_the_given_filename(self):
        path = self.root_dir.full_path
        self.cache.has = mock.MagicMock(return_value=False)
        with mock.patch( 'shutil.copy2', return_value='copied' ) as mock_copy:
            FilesystemCache().put('my_key', path)
            mock_copy.assert_called_with_arguments(path)

    def test_that_when_the_given_key_exists_then_delete_removes_the_file(self):
        with mock.patch( 'os.remove' ) as mock_delete:
            self.cache.has = mock.MagicMock(return_value=True)
            FilesystemCache().delete('my_key')
            mock_delete.assert_called()

    def test_that_when_the_given_key_does_not_exist_then_delete_does_not_call_delete_on_the_key(self):
        with mock.patch( 'os.remove' ) as mock_delete:
            self.cache.has = mock.MagicMock(return_value=False)
            FilesystemCache().delete('my_key')
            self.assertEqual(False, mock_delete.called)

        