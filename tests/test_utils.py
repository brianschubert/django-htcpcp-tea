#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

import unittest

from django.test import RequestFactory, override_settings
from django_htcpcp_tea import utils


class UtilsStatelessTests(unittest.TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_resolve_requested_additions_empty(self):
        request = self.rf.post('/')
        self.assertEqual(utils.resolve_requested_additions(request), [])

    def test_resolve_requested_additions_header(self):
        request = self.rf.post('/', HTTP_ACCEPT_ADDITIONS='Sugar, Half-and-Half')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Sugar', 'Half-and-Half']
        )

    @override_settings(HTCPCP_GET_ADDITIONS=True)
    def test_resolve_requested_additions_header_and_empty_get(self):
        request = self.rf.post('/?', HTTP_ACCEPT_ADDITIONS='Sugar, Half-and-Half')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Sugar', 'Half-and-Half']
        )

    @override_settings(HTCPCP_GET_ADDITIONS=True)
    def test_resolve_requested_additions_header_and_get(self):
        request = self.rf.post('/?Milk&Vanilla', HTTP_ACCEPT_ADDITIONS='Sugar, Half-and-Half')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Sugar', 'Half-and-Half', 'Milk', 'Vanilla']
        )

    @override_settings(HTCPCP_GET_ADDITIONS=True)
    def test_resolve_requested_additions_empty_header_and_get(self):
        request = self.rf.post('/?Milk&Vanilla')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Milk', 'Vanilla']
        )

    @override_settings(HTCPCP_GET_ADDITIONS=False)
    def test_resolve_requested_additions_header_and_ignored_get(self):
        request = self.rf.post('/?Milk&Vanilla', HTTP_ACCEPT_ADDITIONS='Sugar, Half-and-Half')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Sugar', 'Half-and-Half']
        )

    def test_resolve_requested_additions_header_with_odd_spacing(self):
        request = self.rf.post('/', HTTP_ACCEPT_ADDITIONS='Sugar,     Half-and-Half,Milk')
        self.assertEqual(
            utils.resolve_requested_additions(request),
            ['Sugar', 'Half-and-Half', 'Milk']
        )
