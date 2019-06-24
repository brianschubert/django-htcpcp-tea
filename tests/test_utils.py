#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

import unittest

from django.test import RequestFactory, TestCase, override_settings
from django_htcpcp_tea import urls, utils
from django_htcpcp_tea.models import Pot

# URL patterns for UtilsTests
urlpatterns = urls.urlpatterns


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


@override_settings(ROOT_URLCONF=__name__)
class UtilsTests(TestCase):
    fixtures = ['demo_pots', 'rfc_2324_additions', 'rfc_7168_teas']

    def test_build_alternates_no_pot(self):
        alternates = list(utils.build_alternates())

        expected = [
            ('/pot-1/', 'message/coffeepot'),
            ('/pot-2/', 'message/coffeepot'),
            ('/pot-3/darjeeling/', 'message/teapot'),
            ('/pot-3/earl-grey/', 'message/teapot'),
            ('/pot-3/peppermint/', 'message/teapot'),
            ('/pot-4/', 'message/coffeepot'),
            ('/pot-4/darjeeling/', 'message/teapot'),
            ('/pot-4/earl-grey/', 'message/teapot'),
            ('/pot-4/peppermint/', 'message/teapot')
        ]

        self.assertEqual(
            alternates,
            expected,
        )

    def test_build_alternates_for_pot_no_tea(self):
        pot = Pot.objects.get(pk=1)
        alternates = list(utils.build_alternates(index_pot=pot))

        self.assertEqual(
            alternates,
            [('/pot-1/', 'message/coffeepot')]
        )

    def test_build_alternates_for_pot_with_tea(self):
        pot = Pot.objects.get(pk=3)
        alternates = list(utils.build_alternates(index_pot=pot))

        self.assertEqual(
            alternates,
            [
                ('/pot-3/darjeeling/', 'message/teapot'),
                ('/pot-3/earl-grey/', 'message/teapot'),
                ('/pot-3/peppermint/', 'message/teapot'),
            ]
        )
