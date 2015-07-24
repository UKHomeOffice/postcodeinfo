# -*- coding: utf-8 -*-
import os

from Crypto.Hash import SHA512


class SHA512TokenGenerator(object):

    def generate_key(self):
        return SHA512.new(os.urandom(20)).hexdigest().decode()[-40:]


def custom_generate_key(self):
    return SHA512TokenGenerator().generate_key()
