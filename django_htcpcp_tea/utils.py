#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.urls import reverse

from .models import Pot


def build_alternates(index_pot=None):
    """
    Generate the Alternates pairs for available beverages, optionally
    for a specific pot.
    """
    if index_pot:
        pots = (index_pot,)
    else:
        pots = Pot.objects.prefetch_related('supported_teas').all()
    for pot in pots:
        if pot.brew_coffee:
            yield (reverse('pot-detail', args=[pot.id]), 'message/coffeepot')
        for tea in pot.supported_teas.all():
            yield (reverse('pot-detail-tea', args=[pot.id, tea.slug]), 'message/teapot')
