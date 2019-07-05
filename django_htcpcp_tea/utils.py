#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.db.models import Q
from django.urls import reverse

from .models import Pot, ForbiddenCombination
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


def find_forbidden_combinations(requested_additions, tea_slug=None):
    """
    Return the list of ForbiddenCombinations that prohibit some part of the
    requested additions.
    """

    request_additions = set(requested_additions)

    # Calls to ForbiddenCombination.forbids_additions will need the full
    # list of forbidden additions for each retrieved objects.
    forbidden = ForbiddenCombination.objects.prefetch_related('additions')

    if tea_slug:
        forbidden = forbidden.filter(Q(tea__slug=tea_slug) | Q(tea__isnull=True))
    else:
        forbidden = forbidden.filter(tea__isnull=True)

    # Filter ForbiddenCombinations by what additions they forbid in Python
    # since I could not find a way to accomplish this purely in the database.
    return [fc for fc in forbidden if fc.forbids_additions(request_additions)]
