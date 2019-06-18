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
            annotation_name: Count(field)
        })

    def with_tea_count(self):
        return self._count_relation('supported_teas', 'tea_count')

    def with_addition_count(self):
        return self._count_relation('supported_additions', 'addition_count')


class Pot(models.Model):
    """A Tea- or Coffee Pot capable of brewing a choice beverage."""
    name = models.CharField(max_length=35, unique=True)

    brew_coffee = models.BooleanField(verbose_name='able to brew coffee', default=True)

    supported_teas = models.ManyToManyField('TeaType', blank=True)

    supported_additions = models.ManyToManyField('Addition', blank=True)

    objects = PotQuerySet.as_manager()

    @cached_property
    def tea_capable(self):
        return self.supported_teas.exists()

    @property
    def is_teapot(self):
        return self.tea_capable and not self.brew_coffee


class TeaType(models.Model):
    """
    A variety of tea that can be brewed by a pot.

    Per the HTCPCP standard, tea may be available as tea bags or tea leaves.
    """
    name = models.CharField(verbose_name='Tea name', max_length=35, unique=True)

    slug = models.SlugField(unique=True)


class Addition(models.Model):
    """
    A beverage addition that may be specified in the Accept-Additions header
    field of an HTCPCP request.
    """
    name = models.CharField(max_length=35, unique=True)

    def clean(self):
        # Calling parent in case it is given a non-empty body in the
        # future (currently it is empty).
        super().clean()

        error_msg = ("Decaffeinated addition not allowed. RFC 2324 specifies "
                     "no option for decaffeinated coffee. What's the point? ")

        if 'decaffeinated' in self.name.lower():
            raise ValidationError(error_msg)
