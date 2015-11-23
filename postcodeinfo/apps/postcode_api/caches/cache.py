# -*- encoding: utf-8 -*-
"""
Abstract base class for Cache implementations
"""

import re

class Cache:



    def key_for(self, object_identifier):
        """ 
        Default implementation: replace any non a-z / 0-9 chars
        with  an underscore. Opens possibility of collisions,
        but this shouldn't be a problem on the resource names
        we know we'll be dealing with at the moment.
        """
        regex = re.compile("([a-z][A-Z][0-9])+")
        return object_identifier.replace(regex, '_')

    def has(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def get(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def put(self, object_identifier):
        raise NotImplementedError("Subclasses should implement this!")

    def delete(self, key):
        raise NotImplementedError("Subclasses should implement this!")

    def last_modified(self, key):
        raise NotImplementedError("Subclasses should implement this!")        