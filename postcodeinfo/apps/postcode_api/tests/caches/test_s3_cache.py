import mock, os, random, string, tempfile, unittest

from postcode_api.caches.s3_cache import S3Cache


def temp_dir(prefix="test_s3_cache"):
    return tempfile.mkdtemp(prefix=prefix)

def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def temp_file_path():
    return os.path.join(temp_dir(), random_string(8))


class S3CacheTest(unittest.TestCase):
   
    def setUp(self):
        self.mock_key = mock.MagicMock('mock Key')
        self.mock_key.get_contents_to_filename = mock.MagicMock(return_value='contents')
        self.mock_key.set_contents_from_filename = mock.MagicMock(return_value='contents set')
        self.mock_key.delete = mock.MagicMock(return_value='deleted')

    def test_that_when_the_given_key_exists_then_get_calls_get_contents_to_filename(self):
        path = temp_file_path()
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=True)
            S3Cache().get('my_key', path)
            self.mock_key.get_contents_to_filename.assert_called_with_arguments(path)


    def test_that_when_the_given_key_does_not_exist_then_get_does_not_call_get_contents_to_filename(self):
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=False)
            S3Cache().get('my_key', temp_file_path())
            self.assertEqual(False, self.mock_key.get_contents_to_filename.called)

    def test_that_when_the_given_key_exists_then_has_returns_true(self):
        path = temp_file_path()
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=True)
            self.assertEqual(True, S3Cache().has('some key'))

    def test_that_when_the_given_key_does_not_exist_then_has_returns_false(self):
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=False)
            self.assertEqual(False, S3Cache().has('some key'))

    def test_that_put_sets_the_given_cache_key_with_the_contents_of_the_given_filename(self):
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            S3Cache().put('my_key', temp_file_path())
            self.assertEqual(True, self.mock_key.set_contents_from_filename.called)

    def test_that_when_the_given_key_exists_then_delete_calls_delete_on_the_key(self):
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=True)
            S3Cache().delete('my_key')
            self.mock_key.delete.assert_called()

    def test_that_when_the_given_key_does_not_exist_then_delete_does_not_call_delete_on_the_key(self):
        with mock.patch( 'postcode_api.caches.s3_cache.S3Cache._s3_key', return_value=self.mock_key ):
            self.mock_key.exists = mock.MagicMock(return_value=False)
            S3Cache().delete('my_key')
            self.assertEqual(False, self.mock_key.delete.called)

        