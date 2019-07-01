#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from .settings import htcpcp_settings


class HTCPCPTeaMiddleware:

    HTCPCP_MESSAGE_KEYWORDS = (b'start', b'stop')

    def __init__(self, get_response):
        self.get_response = get_response
        self.valid_methods = ('BREW', 'WHEN')
        if htcpcp_settings.ALLOW_DEPRECATED_POST:
            self.valid_methods += ('POST',)

    def __call__(self, request):
        htcpcp_valid = True

        if request.method not in self.valid_methods:
            htcpcp_valid = False

        # Resolve HTCPCP message type (start or stop)
        if htcpcp_settings.STRICT_REQUEST_BODY:
            if request.body not in self.HTCPCP_MESSAGE_KEYWORDS:
                htcpcp_valid = False
            else:
                request.htcpcp_message_type = request.body.decode(encoding='utf-8')
        else:
            for keyword in self.HTCPCP_MESSAGE_KEYWORDS:
                if keyword in request.body:
                    request.htcpcp_message_type = keyword.decode(encoding='utf-8')
                    break  # Trigger else branch if no keyword is found
            else:
                htcpcp_valid = False

        request.htcpcp_valid = htcpcp_valid

        response = self.get_response(request)

        try:
            response['Alternates'] = self.build_alternates(response)
        except AttributeError:
            pass

        update_server_name = htcpcp_settings.OVERRIDE_SERVER_NAME

        if update_server_name:
            if update_server_name is True:
                response['Server'] = 'HTCPCP-TEA ' + request.META['SERVER_SOFTWARE']
            elif callable(update_server_name):
                response['Server'] = update_server_name(request, response)
            else:
                response['Server'] = update_server_name.format(**request.META)

        return response

    def build_alternates(self, response):
        fmt = '{{"{}" {{type {}}}}}'
        return ','.join(
            fmt.format(*pair) for pair in response.htcpcp_alternates
        )
