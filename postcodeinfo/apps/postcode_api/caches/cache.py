# -*- encoding: utf-8 -*-
"""
Abstract base class for Cache implementations
"""


class Cache:

    def has(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def get(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def put(self, key, local_filename):
        raise NotImplementedError("Subclasses should implement this!")

    def delete(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def last_modified(self, key):
        raise NotImplementedError("Subclasses should implement this!")
