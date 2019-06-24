#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.core.exceptions import ValidationError
from django.test import TestCase
from django_htcpcp_tea.models import Addition, Pot


class PotTests(TestCase):
    fixtures = ['demo_pots', 'rfc_2324_additions', 'rfc_7168_teas']

    def test_pot_tea_capable(self):
        pots = Pot.objects.order_by('id').all()
        tea_status = [(p.name, p.tea_capable) for p in pots]

        self.assertEqual(
            tea_status,
            [
                ('French Press', False),
                ("Joe's Joe Jar", False),
                ('Breville (R) BTM800XL', True),
                ('A Talented Cow', True),
            ],
        )

    def test_pot_is_teapot(self):
        pots = Pot.objects.order_by('id').all()
        teapot_status = [(p.name, p.is_teapot) for p in pots]

        self.assertEqual(
            teapot_status,
            [
                ('French Press', False),
                ("Joe's Joe Jar", False),
                ('Breville (R) BTM800XL', True),
                ('A Talented Cow', False),
            ],
        )

    def test_fetch_additions_empty_names(self):
        pot = Pot.objects.get(name="Joe's Joe Jar")
        self.assertEqual(0, len(pot.fetch_additions([])))

    def test_fetch_additions_supports_all_names(self):
        pot = Pot.objects.get(name="Joe's Joe Jar")
        names = ['Cream', 'Half-and-Half', 'Vanilla']

        additions = pot.fetch_additions(names)
        self.assertEqual(
            names,
            [a.name for a in additions],
        )

    def test_fetch_additions_partially_supports_names(self):
        pot = Pot.objects.get(name="A Talented Cow")
        names = ['Cream', 'Half-and-Half', 'Vanilla']

        with self.assertRaises(Addition.DoesNotExist):
            pot.fetch_additions(names)

    def test_fetch_additions_nonexistent_name(self):
        pot = Pot.objects.get(name="A Talented Cow")
        names = ['Wood']

        with self.assertRaises(Addition.DoesNotExist):
            pot.fetch_additions(names)

    def test_fetch_additions_pot_serves_no_additions(self):
        pot = Pot.objects.get(name="French Press")
        names = ['Cream', 'Half-and-Half', 'Vanilla']

        with self.assertRaises(Addition.DoesNotExist):
            pot.fetch_additions(names)

    def test_query_set_with_tea_count(self):
        pots = Pot.objects.with_tea_count().all()
        tea_couts = [(p.name, p.tea_count) for p in pots]
        self.assertEqual(
            tea_couts,
            [
                ('French Press', 0),
                ("Joe's Joe Jar", 0),
                ('Breville (R) BTM800XL', 3),
                ('A Talented Cow', 3),
            ],
        )

    def test_query_set_with_addition_count(self):
        pots = Pot.objects.with_addition_count().all()
        addition_counts = [(p.name, p.addition_count) for p in pots]
        self.assertEqual(
            addition_counts,
            [
                ('French Press', 0),
                ("Joe's Joe Jar", 14),
                ('Breville (R) BTM800XL', 0),
                ('A Talented Cow', 5),
            ],
        )


class AdditionTests(TestCase):
    fixtures = ['rfc_2324_additions']

    def test_is_milk(self):
        milk = Addition.objects.get(name='Cream')
        not_milk = Addition.objects.get(name='Vanilla')

        self.assertTrue(milk.is_milk)
        self.assertFalse(not_milk.is_milk)

    def test_addition_cannot_be_decaffeinated(self):
        with self.assertRaises(ValidationError) as cm:
            addition = Addition(name='decaffeinated')
            addition.clean()

        self.assertIn(
            'no option for decaffeinated coffee',
            cm.exception.message,
        )
