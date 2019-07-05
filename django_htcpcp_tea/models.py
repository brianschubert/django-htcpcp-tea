#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.utils.functional import cached_property


class PotQuerySet(models.QuerySet):
    def _count_relation(self, field, annotation_name):
        return self.annotate(**{
            annotation_name: Count(field, distinct=True)
        })

    def with_tea_count(self):
        return self._count_relation('supported_teas', 'tea_count')

    def with_addition_count(self):
        return self._count_relation('supported_additions', 'addition_count')


class Pot(models.Model):
    """A Tea- or Coffee Pot capable of brewing a choice beverage."""
    name = models.CharField(
        max_length=35,
        unique=True,
        help_text='The name of this pot, e.g. "Joe\'s Joe Jar" or "Breville (R)'
                  ' BTM800XL"',
    )

    brew_coffee = models.BooleanField(
        verbose_name='able to brew coffee',
        default=True,
        help_text="Can this pot brew coffee?",
    )

    supported_teas = models.ManyToManyField(
        'TeaType',
        blank=True,
        related_name='pot_list'
    )

    supported_additions = models.ManyToManyField(
        'Addition',
        blank=True,
        related_name='pot_list'
    )

    objects = PotQuerySet.as_manager()

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

    @cached_property
    def tea_capable(self):
        """Return True if this pot can serve tea."""
        return self.supported_teas.exists()

    @property
    def is_teapot(self):
        """Return True if this pot can serve tea, but cannot serve coffee."""
        return self.tea_capable and not self.brew_coffee

    def fetch_additions(self, addition_names):
        """
        Return the Additions that this pot supports whose names are in the
        provided sequence.

        If this pot does not support an Addition whose name is provided, raise
        an Addition.DoesNotExist error.
        """
        additions = self.supported_additions.filter(name__in=addition_names)
        # Resolve the query set to compute its length.
        # Replace this len() call with a queryset annotation if further
        # filtering becomes necessary.
        if len(addition_names) != len(additions):
            raise Addition.DoesNotExist
        return additions


class TeaType(models.Model):
    """
    A variety of tea that can be brewed by a pot.

    Per the HTCPCP standard, tea may be available as tea bags or tea leaves.
    """
    name = models.CharField(
        verbose_name='Tea name',
        max_length=35,
        unique=True,
        db_index=True,
    )

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Addition(models.Model):
    """
    A beverage addition that may be specified in the Accept-Additions header
    field of an HTCPCP request.
    """

    MILK = 'MLK'

    SYRUP = 'SYP'

    SWEETENER = 'SWT'

    SPICE = 'SPC'

    ALCOHOL = 'ACL'

    SUGAR = 'SUG'

    OTHER = 'OTR'

    TYPE_CHOICES = (
        (MILK, "Milk"),
        (SYRUP, "Syrup"),
        (SWEETENER, "Sweetener"),
        (SPICE, "Spice"),
        (ALCOHOL, "Alcohol"),
        (SUGAR, "Sugar"),
        (OTHER, "Other"),
    )

    name = models.CharField(
        max_length=35,
        unique=True,
        help_text="The name of this beverage addition as it would appear in the"
                  " HTCPCP Accept-Additions header field.",
    )

    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        verbose_name='Addition type',
    )

    def clean(self):
        # Calling parent in case it is given a non-empty body in the
        # future (currently it is empty).
        super().clean()

        error_msg = ("Decaffeinated addition not allowed. RFC 2324 specifies "
                     "no option for decaffeinated coffee. What's the point? ")

        if 'decaffeinated' in self.name.lower():
            raise ValidationError(error_msg)

    def __str__(self):
        return "{} / {}".format(self.get_type_display(), self.name)

    @property
    def is_milk(self):
        return self.type == self.MILK


class ForbiddenCombination(models.Model):
    """
    A combination of additions that is "contrary to the sensibilities of a
    consensus of drinkers", either for a specific variety of tea or for all
    beverages.
    """
    tea = models.ForeignKey(
        TeaType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='forbidden_combinations',
        help_text=("The type of tea that this forbidden combination applies to."
                   " Leave blank to apply to all beverages."),
    )

    additions = models.ManyToManyField(
        Addition,
        related_name='forbidden_combinations'
    )

    reason = models.CharField(max_length=180)

    def __str__(self):
        return '{} / {}'.format(
            'All' if not self.tea else self.tea.name,
            ', '.join(a.name for a in self.additions.all())
        )

    def forbids_additions(self, requested_additions):
        """
        Return True if the combination of additions that this
        ForbiddenCombination prohibits is contained in the specified sequence
        of additions.
        """
        return set(self.additions.all()).issubset(requested_additions)
