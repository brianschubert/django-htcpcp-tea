#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

import django
from django.test import Client

HTCPCP_COFFEE_CONTENT = 'message/coffeepot'

HTCPCP_TEA_CONTENT = 'message/teapot'


class HTCPCPClient(Client):

    def _htcpcp_post(
        self,
        method,
        path,
        data=None,
        content_type=HTCPCP_COFFEE_CONTENT,
        follow=False,
        secure=False,
        **extra
    ):
        """
        Mimic the functionality of Client.post, but allow for the customization
        of the HTTP verb associated with a post-like request.
        """
        if django.VERSION < (2, 1):
            # self._encode_json only exists in Django>=2.1a1
            data = {} if data is None else data
        else:
            data = self._encode_json({} if data is None else data, content_type)
        post_data = self._encode_data(data, content_type)

        response = self.generic(method, path, post_data, content_type, secure=secure, **extra)

        if follow:
            response = self._handle_redirects(response, data=data, content_type=content_type, **extra)
        return response

    def post(self, *args, **kwargs):
        return self._htcpcp_post('POST', *args, **kwargs)

    def brew(self, *args, **kwargs):
        return self._htcpcp_post('BREW', *args, **kwargs)

    def when(self, *args, **kwargs):
        return self._htcpcp_post('WHEN', *args, **kwargs)


def make_tea_url(pot, tea):
    return ''.join((pot.get_absolute_url(), tea.slug, '/'))
