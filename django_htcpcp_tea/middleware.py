#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from .settings import htcpcp_settings
from .utils import render_alternates_header
from .views import brew_pot


class HTCPCPTeaMiddleware:
    HTCPCP_MESSAGE_KEYWORDS = (b'start', b'stop')

    HTCPCP_MIME_TYPES = ('message/teapot', 'message/coffeepot')

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

        if (htcpcp_settings.STRICT_MIME_TYPE and
                request.content_type not in self.HTCPCP_MIME_TYPES):
            htcpcp_valid = False

        request.htcpcp_valid = htcpcp_valid

        if (htcpcp_valid and request.path == '/' and
                htcpcp_settings.OVERRIDE_ROOT_URI and htcpcp_settings.STRICT_MIME_TYPE):
            response = brew_pot(request)
        else:
            response = self.get_response(request)

        try:
            alternates_pairs = response.htcpcp_alternates
            response['Alternates'] = render_alternates_header(alternates_pairs)
        except AttributeError:
            pass

        update_server_name = htcpcp_settings.OVERRIDE_SERVER_NAME

        if update_server_name:
            if update_server_name is True:
                server = request.META.get('SERVER_SOFTWARE')
                response['Server'] = 'HTCPCP-TEA ' + (server if server else 'Python')
            elif callable(update_server_name):
                response['Server'] = update_server_name(request, response)
            else:
                response['Server'] = update_server_name.format(**request.META)

        return response
