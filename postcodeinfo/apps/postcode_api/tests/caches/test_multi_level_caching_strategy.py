# -*- encoding: utf-8 -*-

import mock
import unittest

from postcode_api.caches.multi_level_caching_strategy import MultiLevelCachingStrategy


class MockCache(object):

    def __init__(self, *args, **kwargs):
        self._has = kwargs.pop('has', None)
        self._get = kwargs.pop('get', None)
        self._last_modified = kwargs.pop('last_modified', None)

    def has(self, _):
        return self._has

    def get(self, _key, _filename):
        return self._get

    def last_modified(self, _):
        return self._last_modified


class MultiLevelCachingStrategyTest(unittest.TestCase):

    def setUp(self):
        self.mock_cache_1 = MockCache(
            has=True, get="mocked cache_1 value", last_modified="Tue, 24 Nov 2015 16:37:32 GMT")
        self.mock_cache_2 = MockCache(
            has=False, get="mocked cache_2 value", last_modified="Mon, 24 Nov 2015 16:37:32 GMT")
        self.strategy = MultiLevelCachingStrategy(
            caches=[self.mock_cache_1, self.mock_cache_2])

    def test_that_when_no_cache_has_the_key_then_get_returns_none(self):
        self.mock_cache_1._has = False
        self.mock_cache_2._has = False
        self.assertEqual(None, self.strategy.get('some_key', '/tmp/test_file'))

    def test_that_when_cache_1_has_the_key_but_cache_2_does_not_then_get_returns_it_from_cache_1(self):
        self.strategy.caches[0]._has = True
        self.strategy.caches[1]._has = False

        self.assertEqual(
            "mocked cache_1 value", self.strategy.get('some_key', '/tmp/test_file'))

    def test_that_when_cache_2_has_the_key_but_cache_1_does_not_then_get_returns_it_from_cache_2(self):
        self.mock_cache_1._has = False
        self.mock_cache_2._has = True
        self.assertEqual(
            "mocked cache_2 value", self.strategy.get('some_key', '/tmp/test_file'))

    def test_that_when_both_caches_have_the_key_then_get_returns_the_newest(self):
        self.mock_cache_1._has = True
        self.mock_cache_2._has = True
        self.assertEqual(
            "mocked cache_1 value", self.strategy.get('some_key', '/tmp/test_file'))
