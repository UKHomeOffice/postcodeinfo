from mock import patch

from django.test import TestCase
from rest_framework.authtoken.models import Token

from postcode_api.custom_token_generators import SHA512TokenGenerator

import postcode_api.models


class CustomKeyGeneratorsTestCase(TestCase):

    def test_that_generating_a_key_uses_SHA512(self):
        with patch('postcode_api.custom_token_generators.'
                   'SHA512TokenGenerator.generate_key',
                   return_value='foo') as mock:
            key = Token().generate_key()
            self.assertTrue(mock.called)
            self.assertEqual(key, 'foo')
