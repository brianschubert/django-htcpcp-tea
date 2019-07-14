#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.contrib.admin import AdminSite
from django.test import RequestFactory, TestCase
from django_htcpcp_tea import admin, models


class AdminTests(TestCase):

    def setUp(self) -> None:
        self.site = AdminSite()
        self.request = RequestFactory().get('/')

    def test_pot_admin_list_display(self):
        pot_admin = admin.PotAdmin(models.Pot, self.site)
        self.assertEqual(
            pot_admin.get_list_display(self.request),
            ('id', 'name', 'brew_coffee', 'tea_capable_view', 'tea_count_view', 'addition_count_view')
        )
