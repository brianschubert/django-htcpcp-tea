#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from django.conf import settings as django_settings


class _HTCPCPTeaSettings:

    def __init__(self, settings_prefix):
        self.prefix = settings_prefix

    def __getattribute__(self, item):
        try:
            return getattr(django_settings, '{}_{}'.format(self.SETTINGS_PREFIX, item))
        except AttributeError:
            return object.__getattribute__(self, item)


settings = _HTCPCPTeaSettings('HTCPCP')
