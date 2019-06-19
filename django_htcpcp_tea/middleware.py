#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from .settings import htcpcp_settings


class HTCPCPTeaMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.valid_methods = ('BREW',)
        if htcpcp_settings.ALLOW_DEPRECATED_POST:
            self.valid_methods += ('POST',)

    def __call__(self, request):
        # TODO complete HTCPCP validation
        request.htcpcp_valid = request.method in self.valid_methods

        response = self.get_response(request)

        try:
            response['Alternates'] = self.build_alternates(response)
        except AttributeError:
            pass

        return response

    def build_alternates(self, response):
        fmt = '{{"{}" {{type {}}}}}'
        return ','.join(
            fmt.format(*pair) for pair in response.htcpcp_alternates
        )
