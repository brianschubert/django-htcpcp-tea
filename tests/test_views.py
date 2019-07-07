#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.test import TestCase, override_settings
from django_htcpcp_tea import urls, utils
from django_htcpcp_tea.models import Pot, TeaType

from .utils import (
    HTCPCPClient, HTCPCP_COFFEE_CONTENT, HTCPCP_TEA_CONTENT, make_tea_url,
)

# URL patterns for ViewTests
urlpatterns = urls.urlpatterns


@override_settings(
    HTCPCP_POT_SESSIONS=False,
    ROOT_URLCONF=__name__,
)
class ViewTests(TestCase):
    fixtures = ['demo_pots', 'rfc_2324_additions', 'rfc_7168_teas', ]

    client_class = HTCPCPClient

    def setUp(self) -> None:
        self.pot = Pot.objects.get(pk=4)
        # Select any tea supported by the pot
        self.supported_tea = self.pot.supported_teas.all()[:1].get()
        # Select any tea not supported by the pot
        self.unsupported_tea = TeaType.objects.exclude(
            pk__in=self.pot.supported_teas.all()
        )[:1].get()

    def test_invalid_htcpcp_request(self):
        bad_requests = [
            # GET, PUT, HEAD, DELETE, OPTIONS, PATCH, and TRACE
            # methods are not acceptable HTCPCP verbs
            self.client.get('/'),
            self.client.put('/'),
            self.client.head('/'),
            self.client.delete('/'),
            self.client.options('/'),
            self.client.patch('/'),
            self.client.trace('/'),
            # Missing body
            self.client.post('/'),
            self.client.brew('/'),
            self.client.when('/'),
        ]
        for request in bad_requests:
            self.assertEqual(request.status_code, 404)

    def test_brew_no_pot(self):
        response = self.client.brew('/', data='start')
        self.assertEqual(response.status_code, 300)

        self.assertEqual(
            response['Alternates'],
            utils.render_alternates_header(
                utils.build_alternates(index_pot=None)
            )
        )

    def test_brew_tea_start_tea(self):
        response = self.client.brew(
            make_tea_url(self.pot, self.supported_tea),
            content_type=HTCPCP_TEA_CONTENT,
            data='start'
        )
        self.assertContains(response, b'Brewing', status_code=202)

    def test_brew_tea_start_tea_infer_content_type(self):
        response = self.client.brew(
            make_tea_url(self.pot, self.supported_tea),
            data='start'
        )
        self.assertContains(response, b'Brewing', status_code=202)

    def test_brew_tea_start_unsupported_tea(self):
        response = self.client.brew(
            make_tea_url(self.pot, self.unsupported_tea),
            content_type=HTCPCP_TEA_CONTENT,
            data='start'
        )
        self.assertContains(response, b'not available for this pot', status_code=503)

    def test_brew_coffee_start(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start'
        )
        self.assertContains(response, b'Brewing', status_code=202)
        self.assertEqual(
            response['Alternates'],
            utils.render_alternates_header(utils.build_alternates())
        )

    def test_brew_beverage_stop(self):
        response = self.client.brew(self.pot.get_absolute_url(), data='stop')
        self.assertContains(response, b'Finished', status_code=201)

    def test_brew_beverage_stop_required_milk(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            data='stop',
            HTTP_ACCEPT_ADDITIONS='Cream',
        )
        self.assertContains(response, b'Pouring', status_code=200)

    def test_brew_tea_index(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_TEA_CONTENT,
            data='start'
        )
        self.assertContains(response, b'Options', status_code=300)
        self.assertEqual(
            response['Alternates'],
            utils.render_alternates_header(
                utils.build_alternates(index_pot=self.pot)
            )
        )

    def test_when_stop(self):
        response = self.client.brew(self.pot.get_absolute_url(), data='stop')
        self.assertContains(response, b'Finished', status_code=201)

    def test_when_start(self):
        response = self.client.when(self.pot.get_absolute_url(), data='start')
        self.assertContains(
            response,
            b'Cannot start a beverage with a WHEN request.',
            status_code=400,
        )

    def test_brew_coffee_is_teapot(self):
        teapot = Pot.objects.get(pk=3)
        response = self.client.brew(
            teapot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertEqual(response.status_code, 418)
