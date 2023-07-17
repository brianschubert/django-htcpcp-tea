.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Examples
========

.. warning::

    This documentation has not been updated since 2019.

This document highlights the basic usage of Django HTCPCP-TEA by interacting with it over a command line interface. It is worth noting that since Django HTCPCP-TEA simulates an HTTP extension, there are many other ways to use it beyond a CLI.

In these examples, I will be using the GNU `netcat`_ utility to transmit HTTP requests. Netcat is available for most Unix systems, including MacOS and Linux. Similar utilities are also available for Windows systems.

.. _netcat: http://netcat.sourceforge.net/

For the sake of brevity, this document assumes that you have already installed Django HTCPCP-TEA will the "Schema Compliant" URL configuration (see :ref:`install-schema-compliant`). If you want to follow these examples for with "Standard" installation, add the appropriate prefix to the request line's URI in each HTCPCP request.

.. note::

    These examples interact with a locally run instance of the `Django testing server`_ located at ``example.localhost:8080``. To duplicate this setup, add ``example.localhost`` as a loopback address on your system. On Unix systems, this can be accomplished by adding::

        127.0.0.1 example.localhost

    to your ``/etc/hosts`` file. Then, run the following command from your Django project's root:

    .. code-block:: console

        $ ./manage.py runserver example.localhost:8080

.. _Django testing server: https://docs.djangoproject.com/en/2.2/ref/django-admin/#runserver

Basic HTCPCP
------------

The simplest way to use Django HTCPCP-TEA is with pot sessions disabled. If you have set the ``HTCPCP_POT_SESSION`` setting to ``False``, Django HTCPCP-TEA will not try to keep track of your transaction history with the servers pots, so you do not have to worry about keeping track of a session id.

Let's begin using Django HTCPCP-TEA in this capacity by creating a file named ``request.http`` with the following contents:

.. code-block:: http

    BREW / HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 5

    start

.. note::

    The HTCPCP request listed above uses the ``BREW`` request method from the HTCPCP standard. If this method is not available to you in your HTTP client, the ``POST`` method can be used in place with no loss of functionality.

This is a simple HTCPCP request that will prompt the server to return a list of available beverages. To the untrained eye, this file will look like an ordinary HTTP request: it has a well-formed request line, a Host header, and some entity body. A closer look, however, makes it clear that this request makes us of some unconventional HTTP. Most notably, the request method, found at the beginning of the request line, is ``BREW`` (not a particular common HTTP verb). Moreover, the content type is the HTCPCP specialize ``message/coffee`` pot, and the content itself is just the word "start". These three elements are key to creating a legal HTCPCP request. Get them wrong, and you will most likely be ignored by your digital barista.

You can send this request to an HTCPCP server by running the following netcat command.

.. code-block:: console

    $ nc example.localhost 8080 < request.http

You should receive a response the resembles the listing below.

.. code-block:: http
    :emphasize-lines: 4-7,21-24

    HTTP/1.1 300 Multiple Choices
    Date: Tue, 23 Jul 2019 17:14:51 GMT
    Content-Type: text/html; charset=utf-8
    Alternates: {"/pot-1/" {type message/coffeepot}},
                --snip--
                {"/pot-3/earl-grey" {type message/teapot}},
                --snip--
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 769

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <h1>Options</h1>
        <ul>
            <li><a href="/pot-1/">/pot-1/</a> (type message/coffeepot)</li>
            --snip--
            <li><a href="/pot-3/earl-grey/">/pot-3/earl-grey/</a> (type message/teapot)</li>
            --snip--
        </ul>
    </body>
    </html>


Once again, this is all pretty standard HTTP. The important bits for our purposes are the ``Alternates`` header and the response body. You'll note that the ``Alternates`` header field contains a listing of all of the beverages that are available from each of the pots hosted by the server. A similar, more human-readable listing of the same information is found in the response's body, which is formatted as HTML by default (see :ref:`override_templates` for details on how to customize the format of HTCPCP responses).

From this response, we can see that Pot 1 on the server supports brewing coffee on the ``/pot-1/`` uri, and Pot 3 supports brewing tea on the ``/pot-3/earl-grey/`` uri. This is all the information we need to start requesting beverages from the HTCPCP server.

To brew your first beverage, change the request uri in ``request.http`` to ``/pot-1/``, while leaving the rest of the content the same:

.. code-block:: http

    BREW /pot-1/ HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 5

    start

Send this new request to the server with the same netcat command. You should be greeted with a different output:

.. code-block:: http
    :emphasize-lines: 1,16

    HTTP/1.1 202 Accepted
    Date: Tue, 23 Jul 2019 16:43:17 GMT
    Content-Type: text/html; charset=utf-8
    Alternates: --snip--
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 878

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <p>Brewing coffee...</p>
            <h2>Alternatives, in case you change your mind...</h2>
            <ul>
                --snip--
            </ul>
    </body>
    </html>

This response indicates that you have successfully asked the server to start brewing a pot of coffee. We still received a list of alternatives beverages despite having requested a cup of coffee due to stipulation in `RFC 7168 section 2.1.1`_, which safeguards against the selection of "inferior caffeinated beverages".

.. _RFC 7168 section 2.1.1: https://tools.ietf.org/html/rfc7168#section-2.1.1

.. note::

    Since pot session are disabled for now, repeating the ``BREW`` request above will result in precisely the same response. The server will not remember that it is "already brewing a pot of coffee." This functionality will change once the ``HTCPCP_POT_SESSION`` setting in enabled in Django.

To tell the server to stop brewing your pot of coffee, send the following request by updating ``request.http`` and running the same netcat command:

.. code-block:: http
    :emphasize-lines: 4-6

    BREW /pot-1/ HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 4

    stop

You should receive the following response:

.. code-block:: http
    :emphasize-lines: 1,15-17

    HTTP/1.1 201 Created
    Date: Tue, 23 Jul 2019 17:32:09 GMT
    Content-Type: text/html; charset=utf-8
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 298

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <p>Finished brewing your coffee. Please come and collect your beverage.</p>
        <h2>Additions</h2>
            <p>Your beverage has no additions.</p>
    </body>
    </html>


And voila! Your is coffee is finished and ready for pick-up. You will note, however, that it just black: we did not request any beverage additions yet. Lucky for us, the HTCPCP protocol supports beverage fixations from milk and sugar to spice and booze. This aspect of HTCPCP will be covered in greater detail in :ref:`Adding Additions to your Requests`.

Bringing HTCPCP to Life
-----------------------

Smarter servers means smarter coffee, right?

To truly reap the benefits of Django HTCPCP-TEA, we'll want to enable session tracking for the coffee pots. This can be accomplished setting ``HTCPCP_POT_SESSIONS`` to ``True`` in your Django project settings.

With pot sessions enabled, let's try repeating our brew request from the previous sections. Using netcat, send the following HTCPCP request:

.. code-block:: http

    BREW /pot-1/ HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 5

    start

You should receive a response nearly identical to that produced by the sessionless server, with the excpetion of some added ``Cookie`` headers:

.. code-block:: http
    :emphasize-lines: 8,9

    HTTP/1.1 202 Accepted
    Date: Wed, 31 Jul 2019 15:44:05 GMT
    Content-Type: text/html; charset=utf-8
    Alternates: --snip--
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 346
    Vary: Cookie
    Set-Cookie:  sessionid=mx2ijezvoxid0g4sjrwg2e4l7tssjg2e; expires=Wed, 14 Aug 2019 15:44:05 GMT; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax

    <!DOCTYPE html>
        --snip--
        <p>Brewing coffee...</p>
        --snip--
    </html>

These new ``Cookie`` headers denote your Django session ID (precise values will value), which allows the Django session framework to keep track of users between requests.

Let's try repeating the same brew request, but this time add your ``sessionid`` cookie to the request headers:

.. code-block:: http

    BREW /pot-1/ HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 5
    Cookie: sessionid=YOUR_DJANGO_SESSION_ID

    start

Resubmitting this request the server will result in a different response:

.. code-block:: http
    :emphasize-lines: 1,16,17

    HTTP/1.1 503 Service Unavailable
    Date: Wed, 31 Jul 2019 15:52:35 GMT
    Content-Type: text/html; charset=utf-8
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 236
    Vary: Cookie

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <h1>503 Service Unavailable</h1>
        <p>Pot is busy and cannot start a new beverage.</p>
    </body>
    </html>

The server rejected our request since the pot we specified is currently busy. We can only brew at most one beverage in a given pot at a time.

To finish our beverage, repeat the same stop request as before, but be sure to add the ``sessionid`` cookie in the request headers:

.. code-block:: http

    BREW /pot-1/ HTTP/1.1
    Host: example.localhost
    Content-Type: message/coffeepot
    Content-Length: 4
    Cookie: sessionid=YOUR_DJANGO_SESSION_ID

    stop

As before, we receive a simple "beverage finihsed" notice:

.. code-block:: http

    HTTP/1.1 201 Created
    Date: Tue, 23 Jul 2019 17:32:09 GMT
    Content-Type: text/html; charset=utf-8
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 298

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <p>Finished brewing your coffee. Please come and collect your beverage.</p>
        <h2>Additions</h2>
            <p>Your beverage has no additions.</p>
    </body>
    </html>

After finishing our beverage, Pot 1 is no longer in use and is free to begin serving other HTCPCP requests. For the sake of example, let's try repeating out "stop" request, even though no beverage is being brewed. You should receive the following error message:

.. code-block:: http
    :emphasize-lines: 1,16-19

    HTTP/1.1 400 Bad Request
    Date: Wed, 31 Jul 2019 15:59:03 GMT
    Content-Type: text/html; charset=utf-8
    Server: HTCPCP-TEA WSGIServer/0.2
    X-Frame-Options: SAMEORIGIN
    Content-Length: 379
    Vary: Cookie

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>django_htcpcp_tea</title>
    </head>
    <body>
        <h1>400 Bad Request</h1>
        <p>The operator of the coffee pot could not understand the request.</p>
        <p> Reason: No beverage is being brewed by this pot, but the request did not indicate that a new beverage should be brewed</p>
    </body>
    </html>

Oops. We can't stop a beverage when no beverage is being brewed. That's simple enough to remember.

Requesting Tea
--------------

To be documented.

Adding Additions to HTCPCP Requests
-----------------------------------

To be documented.

Pouring Milk
------------

To be documented.

Other Errors You'll Find in the Wild
------------------------------------

To be documented.

