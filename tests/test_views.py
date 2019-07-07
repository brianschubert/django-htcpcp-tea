#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.test import TestCase, override_settings
from django_htcpcp_tea import urls, utils

from .utils import HTCPCPClient

# URL patterns for ViewTests
urlpatterns = urls.urlpatterns


@override_settings(
    HTCPCP_POT_SESSIONS=False,
    ROOT_URLCONF=__name__,
)
class ViewTests(TestCase):
    fixtures = ['demo_pots', 'rfc_2324_additions', 'rfc_7168_teas', ]

    client_class = HTCPCPClient

    def test_brew_no_pot(self):
        response = self.client.brew('/', data='start')
        self.assertEqual(response.status_code, 300)

        self.assertEqual(
            response['Alternates'],
            utils.render_alternates_header(
                utils.build_alternates(index_pot=None)
            )
        )

    def test_when_with_start_body(self):
        response = self.client.when('/pot-1/', data='start')
        self.assertContains(
            response,
            b'Cannot start a beverage with a WHEN request.',
            status_code=400,
        )
