#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from datetime import datetime
from functools import wraps

from django.http import BadHeaderError, Http404
from django.shortcuts import get_object_or_404, render

from .models import Pot
from .settings import htcpcp_settings
from .utils import build_alternates, resolve_requested_additions


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
        response = render(request, 'django_htcpcp_tea/options.html', status=300)
        response.htcpcp_alternates = build_alternates()
        return response

    if request.method == 'WHEN' and request.htcpcp_message_type == 'start':
        return render(
            request,
            'django_htcpcp_tea/400.html',
            {'error_reason': 'Cannot start a beverage with a WHEN request.'},
            status=400
        )

    pot = get_object_or_404(
        Pot.objects.prefetch_related('supported_additions'),
        id=pot_designator,
    )

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
                "should have invalidated this HTCPCP request because of this "
                "discrepancy. If you are receiving this error on a live server,"
                " please notify the developers so that this issue can be "
                "looked into. \n"
                "Received Content-Type: {}".format(request.content_type)
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
    if pot.is_teapot:
        return render(request, 'django_htcpcp_tea/418.html', status=418)

    if not pot.brew_coffee:
        return render(
            request,
            'django_htcpcp_tea/503.html',
            {'error_reason': 'Pot out of service. No coffee or tea available.'},
            status=503,
        )

    return _finalize_beverage(request, pot, 'Coffee')


def _render_teapot(request, pot, tea):
    if request.htcpcp_message_type == 'start':
        # Stop requests sent without a tea type should be respected
        if not tea:
            response = render(request, 'django_htcpcp_tea/options.html', status=300)
            response.htcpcp_alternates = build_alternates(index_pot=pot)
            return response
        elif tea not in pot.supported_teas.values_list('name'):
            return render(
                request,
                'django_htcpcp_tea/503.html',
                {'error_reason': '{} is not available for this pot'.format(tea.capitalize)},
                status=503,
        )
    # Beverage name only required when starting a new beverage
    beverage_name = '{} Tea'.format(tea.capitalize) if tea else None
    return _finalize_beverage(request, pot, beverage_name)


def _finalize_beverage(request, pot, beverage_name):
    additions = resolve_requested_additions(request)
    if not pot.serves_additions(additions):
        return render(request, 'django_htcpcp_tea/406.html', status=406)

    if htcpcp_settings.POT_SESSIONS:
        session_key = 'htcpcp_pot_{}'.format(pot.id)
        pot_status = request.session.get(session_key)

        if pot_status:
            if request.htcpcp_message_type == 'start':
                response = render(
                    request,
                    'django_htcpcp_tea/503.html',
                    {'error_reason': 'Pot is busy and cannot start a new beverage.'},
                    status=503,
                )
            else:  # htcpcp_message_type == 'stop'
                # TODO add logic for pouring milk and handling WHEN method
                # TODO add brew time and additions display to finished tempate
                response = render(request, 'django_htcpcp_tea/finished.html', status=200)
                del request.session[session_key]
        elif request.htcpcp_message_type == 'start':
            # New session, and the client requested a new beverage
            response = render(
                request,
                'django_htcpcp_tea/brewing.html',
                {'beverage': beverage_name},
                status=202,  # Accepted
            )
            request.session[session_key] = {
                'additions': additions,
                'start_time': datetime.utcnow().timestamp()
            }
        else:
            reason = ("No beverage is being brewed by this pot, but the "
                      "request did not indicate that a new beverage should be "
                      "brewed")
            response = render(request, 'django_htcpcp_tea/400.html', {'error_reason': reason}, status=400)
    else:
        # Simulate stateless pot functionality
        if request.htcpcp_message_type == 'start':
            response = render(
                request,
                'django_htcpcp_tea/brewing.html',
                {'beverage': beverage_name},
                status=202,  # Accepted
            )
        else:  # request.htcpcp_message_type == 'stop':
            if request.method == 'WHEN':
                response = render(request, 'django_htcpcp_tea/finished.html', status=200)  # Ok
            elif pot.supported_milks.intersection(additions):
                response = render(request, 'django_htcpcp_tea/pouring.html', status=100)  # Continue
            else:
                response = render(request, 'django_htcpcp_tea/finished.html', status=200)  # Ok

    return response


if htcpcp_settings.DISABLE_CSRF:
    # Mark the HTCPCP view function as being exempt from the CSRF view
    # protection. This is the same as using the csrf_exempt decorator
    # from django.views.decorators.csrf.
    brew_pot.csrf_exempt = True
