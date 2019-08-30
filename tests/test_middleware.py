#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

import unittest

from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django_htcpcp_tea.middleware import HTCPCPTeaMiddleware

from .utils import HTCPCP_COFFEE_CONTENT


class MiddlewareTests(unittest.TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_validate_request_when_method_post(self):
        for condition in (True, False):
            with override_settings(HTCPCP_ALLOW_DEPRECATED_POST=condition):
                checker = self._make_assert_htcpcp_valid(is_valid=condition)
                # Check if POST request is considered to be valid HTCPCP
                request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')
                HTCPCPTeaMiddleware(get_response=checker)(request)

    @override_settings(HTCPCP_STRICT_REQUEST_BODY=True)
    def test_with_strict_request_body(self):
        valid_data = ['start', 'stop']
        invalid_data = ['please start', 'start stop', 'lemon']

        checker = self._make_assert_htcpcp_valid(is_valid=True)
        middleware = HTCPCPTeaMiddleware(get_response=checker)
        for payload in valid_data:
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data=payload)
            middleware(request)

        checker = self._make_assert_htcpcp_valid(is_valid=False)
        middleware = HTCPCPTeaMiddleware(get_response=checker)
        for payload in invalid_data:
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data=payload)
            middleware(request)

    @override_settings(HTCPCP_STRICT_REQUEST_BODY=False)
    def test_with_nonstrict_request_body(self):
        valid_data = ['start', 'stop', 'please start', 'canyoustopnow']
        invalid_data = ['lemon', 'Stop']

        checker = self._make_assert_htcpcp_valid(is_valid=True)
        middleware = HTCPCPTeaMiddleware(get_response=checker)
        for payload in valid_data:
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data=payload)
            middleware(request)

        checker = self._make_assert_htcpcp_valid(is_valid=False)
        middleware = HTCPCPTeaMiddleware(get_response=checker)
        for payload in invalid_data:
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data=payload)
            middleware(request)

    @override_settings(HTCPCP_OVERRIDE_SERVER_NAME=True)
    def test_override_server_name_true(self):
        middleware = HTCPCPTeaMiddleware(lambda request: HttpResponse())
        request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')

        # Remove server software key if it exists
        request.META.pop('SERVER_SOFTWARE', None)

        self.assertEqual(
            middleware(request)['Server'],
            'HTCPCP-TEA Python',
        )

        request.META['SERVER_SOFTWARE'] = 'Squirrel With a Paintbrush'
        self.assertEqual(
            middleware(request)['Server'],
            'HTCPCP-TEA Squirrel With a Paintbrush',
        )

    @override_settings(HTCPCP_OVERRIDE_SERVER_NAME=True)
    def test_override_server_name_ignores_invalid(self):
        def get_response(request):
            response = HttpResponse()
            response['Server'] = 'Normal Server Name'
            return response

        middleware = HTCPCPTeaMiddleware(get_response=get_response)
        invalid_request = self.rf.get('/')

        # Ensure server name is not overridden when the request is not a valid
        # HTCPCP request.
        self.assertEqual(
            middleware(invalid_request)['Server'],
            'Normal Server Name',
        )


    def test_override_server_name_callable(self):
        middleware = HTCPCPTeaMiddleware(lambda request: HttpResponse())
        request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')

        def server_name(request, response):
            return "Server Name Callable"

        with override_settings(HTCPCP_OVERRIDE_SERVER_NAME=server_name):
            self.assertEqual(
                middleware(request)['Server'],
                'Server Name Callable',
            )

    def test_override_server_name_string(self):
        middleware = HTCPCPTeaMiddleware(lambda request: HttpResponse())
        request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')

        request.META['SQUIRREL_TAIL_COLOR'] = 'Acorn Brown'
        fmt = 'Squirrel with a {SQUIRREL_TAIL_COLOR} tail'

        with override_settings(HTCPCP_OVERRIDE_SERVER_NAME=fmt):
            self.assertEqual(
                middleware(request)['Server'],
                'Squirrel with a Acorn Brown tail',
            )

    def test_override_server_name_false(self):
        def get_response(request):
            response = HttpResponse()
            response['Server'] = 'Normal Server Name'
            return response

        middleware = HTCPCPTeaMiddleware(get_response=get_response)
        request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')

        with override_settings(HTCPCP_OVERRIDE_SERVER_NAME=False):
            self.assertEqual(
                middleware(request)['Server'],
                'Normal Server Name',
            )

    def test_override_content_type(self):
        def get_response(request):
            return HttpResponse('Hello', content_type='text/plain')

        middleware = HTCPCPTeaMiddleware(get_response=get_response)

        valid_request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')
        invalid_request = self.rf.get('/')

        with override_settings(HTCPCP_RESPONSE_CONTENT_TYPE=None):
            for r in (valid_request, invalid_request):
                self.assertEqual(
                    middleware(r)['Content-Type'],
                    'text/plain',
                )

        with override_settings(HTCPCP_RESPONSE_CONTENT_TYPE='something/special'):
            self.assertEqual(
                middleware(valid_request)['Content-Type'],
                'something/special',
            )
            self.assertEqual(
                middleware(invalid_request)['Content-Type'],
                'text/plain',
            )

    def test_strict_mine_types(self):
        for condition in (True, False):
            with override_settings(HTCPCP_STRICT_MIME_TYPE=condition):
                checker = self._make_assert_htcpcp_valid(is_valid=not condition)
                # Check if request with non-HTCPCP MIME type valid when
                # STRICT_MINE_TYPE is disabled, but valid when it is enabled.
                request = self.rf.post('/', content_type='message/other', data='start')
                HTCPCPTeaMiddleware(get_response=checker)(request)

    def _make_assert_htcpcp_valid(self, is_valid=True):
        def _assert_htcpcp_valid(request):
            self.assertEqual(request.htcpcp_valid, is_valid)
            return HttpResponse()

        return _assert_htcpcp_valid


class MiddlewareDBTests(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    @override_settings(HTCPCP_STRICT_MIME_TYPE=True)
    def test_override_root(self):
        with override_settings(HTCPCP_OVERRIDE_ROOT_URI=True):
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')
            response = HTCPCPTeaMiddleware(lambda request: HttpResponse('Ok'))(request)
            self.assertContains(response, 'Options', status_code=300)

        with override_settings(HTCPCP_OVERRIDE_ROOT_URI=False):
            request = self.rf.post('/', content_type=HTCPCP_COFFEE_CONTENT, data='start')
            response = HTCPCPTeaMiddleware(lambda request: HttpResponse('Ok'))(request)
            self.assertContains(response, 'Ok', status_code=200)
