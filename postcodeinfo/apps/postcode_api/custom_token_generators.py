# -*- coding: utf-8 -*-
import os

from Crypto.Hash import SHA512


class SHA512KeyGenerator(object):
    def generate(self):
        return SHA512.new(os.urandom(20)).hexdigest().decode()[-40:]

def generate_sha512_key(self):
    return SHA512KeyGenerator().generate()
