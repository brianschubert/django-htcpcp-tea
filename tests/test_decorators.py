#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

import unittest

from django.http import Http404, HttpRequest, HttpResponse
from django.test import override_settings
from django_htcpcp_tea import decorators


class DecoratorTests(unittest.TestCase):

    def test_invalid_htcpcp_request(self):
        @decorators.require_htcpcp
        def mock_view(request):
            return HttpResponse()

        valid_request = HttpRequest()
        valid_request.htcpcp_valid = True

        invalid_request = HttpRequest()
        invalid_request.htcpcp_valid = False

        self.assertEqual(mock_view(valid_request).status_code, 200)
        with self.assertRaises(Http404):
            mock_view(invalid_request)

    def test_safe_condition(self):
        @decorators.safe_condition('no-loose-clothing')
        def mock_view(request):
            return HttpResponse()

        request = HttpRequest()

        with override_settings(HTCPCP_USE_SAFE_HEADER_EXT=True):
            self.assertEqual(mock_view(request)['Safe'], 'if-no-loose-clothing')

        with override_settings(HTCPCP_USE_SAFE_HEADER_EXT=False):
            self.assertIsNone(mock_view(request).get('Safe'))

    def test_safe_require_user_awake(self):
        @decorators.safe_require_user_awake
        def mock_view(request):
            return HttpResponse()

        request = HttpRequest()

        with override_settings(HTCPCP_USE_SAFE_HEADER_EXT=True):
            self.assertEqual(mock_view(request)['Safe'], 'if-user-awake')

        with override_settings(HTCPCP_USE_SAFE_HEADER_EXT=False):
            self.assertIsNone(mock_view(request).get('Safe'))
