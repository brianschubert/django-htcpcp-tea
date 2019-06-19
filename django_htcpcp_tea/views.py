#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from functools import wraps

from django.http import BadHeaderError, Http404, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Pot
from .settings import htcpcp_settings


def require_htcpcp(func):
    """Decorator to make a view only respond to valid HTCPCP requests."""

    @wraps(func)
    def _require_htcpcp(request, *args, **kwargs):
        if not request.htcpcp_valid:
            raise Http404
        return func(request, *args, **kwargs)

    return _require_htcpcp


@require_htcpcp
def brew_pot(request, pot_designator=None, tea_type=None):
    if not pot_designator:
        # TODO add optional templated content
        response = HttpResponse('You have options', status=300)
        # TODO add accept-additions handling
        response.htcpcp_accept_additions = []
        return response

    pot = get_object_or_404(Pot, id=pot_designator)

    if htcpcp_settings.STRICT_MIME_TYPE:
        # Use the request's MIME type to unambiguously categorize the request
        if request.content_type == 'message/coffeepot':
            return _render_coffee(request, pot)
        elif request.content_type == 'message/teapot':
            return _render_teapot(request, pot, tea_type)
        else:
            raise BadHeaderError(
                "The HTCPCP server is running with strict content-types "
                "enabled, but the request's Content-Type was not one of "
                "( message/coffeepot | message/teapot ). The HTCPCP middleware "
                "should have invalidated this HTCPCP request in light of this "
                "discrepancy. If you are receiving this error on a live server,"
                " please notify the developers so that this issue can be "
                "looked into."
            )
    else:
        # Non-HTCPCP MIME types are allowed, so the HTCPCP version
        # must be inferred
        if tea_type:
            # Assume HTCPCP-TEA request, since a tea type was specified
            return _render_teapot(request, pot, tea_type)
        else:
            # Either a standard HTCPCP request, or a HTCPCP-TEA index request
            if request.content_type == 'message/teapot':
                return _render_teapot(request, pot, tea_type)
            else:
                # Default to standard HTCPCP specification.
                # Let's brew some COFFEE!
                return _render_coffee(request, pot)


def _render_coffee(request, pot):
    # TODO add templated content for all responses
    # TODO add Accept-Additions handling
    if pot.is_teapot:
        return HttpResponse('I\'m a tea pot', status=418)

    if not pot.brew_coffee:
        return HttpResponse('Pot out of service. No coffee or tea available.', status=503)

    # TODO "start" / "stop" brewing based on user session for this pot
    # Temporary logic to simulate basic pot functionality
    if request.method == 'WHEN':
        response = HttpResponse('Milk poured', status=200)  # Ok
    elif 'stop' in request.body:
        # TODO check for milk in additions
        response = HttpResponse('Pouring milk, say WHEN', status=100)  # Continue
    else:
        response = HttpResponse('Brewing', status=202)  # Accepted
    return response


def _render_teapot(request, pot, tea):
    pass


if htcpcp_settings.DISABLE_CSRF:
    # Mark the HTCPCP view function as being exempt from the CSRF view
    # protection. This is the same as using the csrf_exempt decorator
    # from django.views.decorators.csrf.
    brew_pot.csrf_exempt = True
