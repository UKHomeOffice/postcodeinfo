# -*- coding: utf-8 -*-
import binascii
import os

from Crypto.Hash import SHA256, SHA512

class DefaultTokenGenerator(object):

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()


class SHA256TokenGenerator(object):

    def generate_key(self):
        return SHA256.new(os.urandom(20)).hexdigest().decode()

class SHA512TokenGenerator(object):

    def generate_key(self):
        return SHA512.new(os.urandom(20)).hexdigest().decode()[-40:]

def custom_generate_key(self):
    return SHA512TokenGenerator().generate_key()
