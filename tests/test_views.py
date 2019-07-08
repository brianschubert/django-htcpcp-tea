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


@override_settings(ROOT_URLCONF=__name__)
class BaseViewTests(TestCase):
    fixtures = [
        'demo_pots',
        'rfc_2324_additions',
        'rfc_7168_teas',
        'demo_forbidden_combinations'
    ]

    client_class = HTCPCPClient

    def setUp(self) -> None:
        self.pot = Pot.objects.get(pk=4)
        # Select any tea supported by the pot
        self.supported_tea = self.pot.supported_teas.all()[:1].get()
        # Select any tea not supported by the pot
        self.unsupported_tea = TeaType.objects.exclude(
            pk__in=self.pot.supported_teas.all()
        )[:1].get()


@override_settings(HTCPCP_POT_SESSIONS=False)
class ViewTests(BaseViewTests):

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

    @override_settings(HTCPCP_CHECK_FORBIDDEN=True)
    def test_brew_coffee_with_forbidden_additions(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
            HTTP_ACCEPT_ADDITIONS='Cream, Skim'
        )
        self.assertContains(response, b"both cream and skim milk!", status_code=403)

    def test_brew_coffee_with_additions(self):
        pot = Pot.objects.get(pk=2)
        # Stop brewing the beverage
        response = self.client.brew(
            pot.get_absolute_url() + '?Rum',
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
            HTTP_ACCEPT_ADDITIONS='Chocolate, Vanilla',
        )
        self.assertContains(response, b'Finished', status_code=201)

        for addition in (b'Rum', b'Chocolate', b'Vanilla'):
            self.assertIn(addition, response.content)

        self.assertNotIn(b'Raspberry', response.content)

    def test_brew_coffee_with_invalid_additions(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
            HTTP_ACCEPT_ADDITIONS='Salt, Whale-Oil'
        )
        self.assertContains(response, b'Not Acceptable', status_code=406)


@override_settings(HTCPCP_POT_SESSIONS=True)
class ViewSessionsTests(BaseViewTests):

    def test_stop_brewing_a_nonexistent_beverage(self):
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'No beverage is being brewed by this pot', status_code=400)

    def test_coffee_cycle(self):
        response = self.client.brew(
            '/',
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )

        self.assertEqual(
            response['Alternates'],
            utils.render_alternates_header(utils.build_alternates())
        )
        self.assertContains(response, b'Options', status_code=300)

        # Start brewing a beverage
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertContains(response, b'Brewing', status_code=202)

        # Attempt to start a new beverage in a busy pot
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertContains(response, b'Pot is busy', status_code=503)

        # Stop brewing (no milk to be poured)
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'Finished', status_code=201)

        # Ensure that the beverage cannot be stopped twice
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'No beverage is being brewed by this pot', status_code=400)

        # Ensure that the pot is now free to begin a new beverage
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertContains(response, b'Brewing', status_code=202)

    def test_coffee_cycle_with_milk(self):
        # Start brewing a beverage with milk addition
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
            HTTP_ACCEPT_ADDITIONS='Cream'
        )
        self.assertContains(response, b'Brewing', status_code=202)

        # Attempt to start a new beverage in a busy pot
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertContains(response, b'Pot is busy', status_code=503)

        # Attempt to say "WHEN!" before milk is poured
        response = self.client.when(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'No milk is being poured', status_code=400)

        # Stop brewing (milk need to be poured)
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'Pouring', status_code=200)

        # Attempt to stop beverage while pouring milk
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'Milk is currently being poured', status_code=400)

        # Say "WHEN!"
        response = self.client.when(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'Finished', status_code=201)

        # Ensure that milk pouring was stopped
        response = self.client.when(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'No beverage is being brewed', status_code=400)

        # Ensure that the pot is now free to begin a new beverage
        response = self.client.brew(
            self.pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
        )
        self.assertContains(response, b'Brewing', status_code=202)

    def test_coffee_cycle_remembers_additions(self):
        # Fetch a pot that supports non-milk additions
        pot = Pot.objects.get(pk=2)
        # Start brewing a beverage with multiple addition
        response = self.client.brew(
            pot.get_absolute_url() + '?Rum',
            content_type=HTCPCP_COFFEE_CONTENT,
            data='start',
            HTTP_ACCEPT_ADDITIONS='Chocolate, Vanilla'
        )
        self.assertContains(response, b'Brewing', status_code=202)

        # Stop brewing the beverage
        response = self.client.brew(
            pot.get_absolute_url(),
            content_type=HTCPCP_COFFEE_CONTENT,
            data='stop',
        )
        self.assertContains(response, b'Finished', status_code=201)

        for addition in (b'Rum', b'Chocolate', b'Vanilla'):
            self.assertIn(addition, response.content)

        self.assertNotIn(b'Raspberry', response.content)
