#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.urls import reverse

from .models import Pot
from .settings import htcpcp_settings


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


def resolve_requested_additions(request):
    """
    Return to requested additions for the provided request.

    Additions may be requested in the ``Accept-Additions`` header field, or
    (if the ``HTCPCP_GET_ADDITIONS`` settings is enabled) in the query string
    of a uri.

    Note that the returned additions are not guaranteed to be valid additions
    that are supported by any pot.
    """
    try:
        header = request.META['HTTP_ACCEPT_ADDITIONS']
        additions = [addition.strip() for addition in header.split(',')]
    except KeyError:
        additions = []

    if htcpcp_settings.GET_ADDITIONS:
        additions += request.GET.dict().keys()

    return additions
