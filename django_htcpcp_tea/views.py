#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from datetime import datetime
from functools import wraps

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Addition, Pot
from .settings import htcpcp_settings
from .utils import (
    build_alternates, find_forbidden_combinations, resolve_requested_additions
)


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

    pot = get_object_or_404(Pot, id=pot_designator)

    if _request_for_tea(request, tea_type):
        response = _precheck_teapot(request, pot, tea_type)
        # Beverage name only required when starting a new beverage
        beverage_name = '{} Tea'.format(tea_type.capitalize) if tea_type else None
    else:
        response = _precheck_coffee(request, pot)
        beverage_name = 'coffee'

    if response is None:
        addition_names = resolve_requested_additions(request)
        try:
            additions = list(pot.fetch_additions(addition_names))
        except Addition.DoesNotExist:
            # Fetch all supported additions for the requested pot.
            # Note that this will result in an additional query.
            context = {'supported_additions': pot.supported_additions.all()}
            return render(request, 'django_htcpcp_tea/406.html', context, status=406)

        if htcpcp_settings.CHECK_FORBIDDEN:
            forbidden = find_forbidden_combinations(additions, tea_type)

            if forbidden:
                context = {'matched_combinations': forbidden}
                return render(request, "django_htcpcp_tea/403.html", context, status=403)

        if htcpcp_settings.POT_SESSIONS:
            response = _finalize_beverage_with_session(request, pot, beverage_name, additions)
        else:
            response = _finalize_beverage(request, pot, beverage_name, additions)

    return response


def _request_for_tea(request, tea_type):
    """
    Determine whether the given request is for tea.

    If the ``STRICT_MIME_TYPE`` settings is enabled, then the MIME type of the
    request is used to unambiguously categorize it as a tea or coffee request.

    If strict MIME types are not enforced, the requested beverage type is
    inferred from the existence of a tea type in the request URI and the HTCPCP
    MIME type, if one is provided.
    """
    if request.content_type == 'message/teapot':
        return True
    elif not htcpcp_settings.STRICT_MIME_TYPE:
        return tea_type
    else:
        return False


def _precheck_coffee(request, pot):
    """
    Return a response if a precondition for coffee requests is not satisfied,
    else None.
    """
    if pot.is_teapot:
        return render(request, 'django_htcpcp_tea/418.html', status=418)

    if not pot.brew_coffee:
        return render(
            request,
            'django_htcpcp_tea/503.html',
            {'error_reason': 'Pot out of service. No coffee or tea available.'},
            status=503,
        )

    return None


def _precheck_teapot(request, pot, tea):
    """
    Return a response if a precondition for tea requests is not satisfied, else
    None.
    """
    if request.htcpcp_message_type == 'start':
        if not tea:  # Require tea type only when starting a new beverage
            alternatives = build_alternates(index_pot=pot)
            context = {'alternatives': alternatives}
            response = render(request, 'django_htcpcp_tea/options.html', context, status=300)
            response.htcpcp_alternates = alternatives
            return response
        elif tea not in pot.supported_teas.values_list('name'):
            return render(
                request,
                'django_htcpcp_tea/503.html',
                {'error_reason': '{} is not available for this pot'.format(tea.capitalize)},
                status=503,
            )
    return None


def _finalize_beverage(request, pot, beverage_name, additions):
    """
    Return a response to the beverage request according to the HTCPCP standard
    without referencing the user's session.
    """
    context = {
        'pot': pot,
        'beverage': beverage_name,
        'additions': additions,
    }

    if request.htcpcp_message_type == 'start':
        if beverage_name == 'coffee':
            # Display alternatives when brewing coffee per RFC 7168 section 2.1.1
            context['alternatives'] = build_alternates(index_pot=pot)
        response = render(request, 'django_htcpcp_tea/brewing.html', context, status=202)  # Accepted
    else:  # request.htcpcp_message_type == 'stop':
        if any(addition.is_milk for addition in additions):
            response = render(request, 'django_htcpcp_tea/pouring.html', context, status=200)  # Ok
        else:
            response = render(request, 'django_htcpcp_tea/finished.html', context, status=201)  # Created

    return response


def _finalize_beverage_with_session(request, pot, beverage_name, additions):
    """
    Return a response to the beverage request according to the HTCPCP standard
    by referencing the current state of the user's session.
    """
    session_key = 'htcpcp_pot_{}'.format(pot.id)
    pot_status = request.session.get(session_key)

    context = {
        'pot': pot,
        'beverage': beverage_name,
        'additions': additions,
    }

    # TODO add brew time and additions display to finished template

    if pot_status:
        # 'stop' requests may not be able to reproduce the name of a beverage
        # or the additions that were requested, so override these values in the
        # context with the ones stored in the user's session.
        context['beverage'] = pot_status['beverage']
        context['additions'] = pot_status['additions']

        if request.htcpcp_message_type == 'start':
            context['error_reason'] = 'Pot is busy and cannot start a new beverage.'
            response = render(request, 'django_htcpcp_tea/503.html', context, status=503)
        else:  # htcpcp_message_type == 'stop'
            if request.method == 'WHEN':
                if pot_status['currently_pouring']:
                    response = render(request, 'django_htcpcp_tea/finished.html', context, status=201)
                    del request.session[session_key]
                else:
                    context['error_reason'] = 'No milk is being poured. Please stop shouting "WHEN!"'
                    return render(request, 'django_htcpcp_tea/400.html', context, status=400)
            else:
                if pot_status['currently_pouring']:
                    context['error_reason'] = 'Milk is currently being poured. Please say "WHEN"'
                    response = render(
                        request, 'django_htcpcp_tea/400.html', context, status=400)
                elif pot_status['needs_milk']:  # Stop brewing and begin pouring milk
                    response = render(request, 'django_htcpcp_tea/pouring.html', context, status=200)
                    request.session[session_key].update({
                        'needs_milk': False,
                        'currently_pouring': True,
                    })
                    request.session.modified = True
                else:  # Stop brewing. No milk required.
                    response = render(request, 'django_htcpcp_tea/finished.html', context, status=201)
                    del request.session[session_key]
    elif request.htcpcp_message_type == 'start':
        # New session, and the client requested a new beverage
        if beverage_name == 'coffee':
            # Display alternatives when brewing coffee per RFC 7168 section 2.1.1
            context['alternatives'] = build_alternates(index_pot=pot)
        response = render(request, 'django_htcpcp_tea/brewing.html', context, status=202)  # Accepted
        request.session[session_key] = {
            'beverage': beverage_name,
            # Serialize the requested additions to as dictionaries for storage
            # in the user's session since we do not need actual Addition objects
            # to display the additions during future requests.
            'additions': [{'name': a.name, 'get_type_display': a.get_type_display()} for a in additions],
            'needs_milk': any(addition.is_milk for addition in additions),
            'currently_pouring': False,
            'start_time': datetime.utcnow().timestamp()
        }
    else:
        reason = ("No beverage is being brewed by this pot, but the "
                  "request did not indicate that a new beverage should be "
                  "brewed")
        response = render(request, 'django_htcpcp_tea/400.html', {'error_reason': reason}, status=400)

    return response


if htcpcp_settings.DISABLE_CSRF:
    # Mark the HTCPCP view function as being exempt from the CSRF view
    # protection. This is the same as using the csrf_exempt decorator
    # from django.views.decorators.csrf.
    brew_pot.csrf_exempt = True
