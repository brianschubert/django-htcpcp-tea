#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.
from functools import wraps

from django.http import Http404

from .settings import htcpcp_settings


def require_htcpcp(func):
    """Decorator to make a view only respond to valid HTCPCP requests."""

    @wraps(func)
    def _require_htcpcp(request, *args, **kwargs):
        if not request.htcpcp_valid:
            raise Http404
        return func(request, *args, **kwargs)

    return _require_htcpcp


def safe_condition(token):
    """
    Decorator for adding a ``Safe`` header to a view's response to indicate
    client conditions for the safe handling of a device that brews coffee.

    The decorator will only have effect if the HTCPCP Safe header extension
    option is enabled.

    See `RFC 2324 section 2.2.1.1`_ for further details.

    .. _RFC 2324 section 2.2.1.1: https://tools.ietf.org/html/rfc2324#section-2.2.1.1
    """
    def decorator(func):
        @wraps(func)
        def _wrapped_view(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            if htcpcp_settings.USE_SAFE_HEADER_EXT:
                response['Safe'] = 'if-{}'.format(token)
            return response

        return _wrapped_view

    return decorator


safe_require_user_awake = safe_condition('user-awake')
"""
Decorator for adding an "if-user-awake" safe condition to the Safe header
field.

See `RFC 2324 section 2.2.1.1`_ for further details.

.. _RFC 2324 section 2.2.1.1: https://tools.ietf.org/html/rfc2324#section-2.2.1.1
"""

