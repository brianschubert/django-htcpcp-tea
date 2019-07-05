#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.conf import settings as django_settings


class _HTCPCPTeaSettings:
    """
    Proxy to the standard Django settings that provides defaults for some
    of this app's settings.
    """

    ALLOW_DEPRECATED_POST = True

    CHECK_FORBIDDEN = True

    DISABLE_CSRF = True

    GET_ADDITIONS = True

    OVERRIDE_SERVER_NAME = True

    POT_SESSIONS = True

    STRICT_MIME_TYPE = True

    STRICT_REQUEST_BODY = False

    def __init__(self, settings_prefix):
        self.prefix = settings_prefix

    def __getattribute__(self, item):
        try:
            return getattr(django_settings, '{}_{}'.format(
                object.__getattribute__(self, 'prefix'),
                item,
            ))
        except AttributeError:
            return object.__getattribute__(self, item)


htcpcp_settings = _HTCPCPTeaSettings('HTCPCP')
