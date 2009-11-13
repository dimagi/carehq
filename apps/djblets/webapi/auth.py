#
# auth.py -- Authentication helpers for webapi
#
# Copyright (c) 2007-2009  Christian Hammond
# Copyright (c) 2007-2009  David Trowbridge
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from datetime import datetime

from django.contrib import auth
from django.views.decorators.http import require_POST

from djblets.webapi.core import WebAPIResponse, WebAPIResponseError
from djblets.webapi.decorators import webapi
from djblets.webapi.errors import LOGIN_FAILED


@require_POST
@webapi
def account_login(request, apitype="json"):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    user = auth.authenticate(username=username, password=password)

    if not user or not user.is_active:
        return WebAPIResponseError(request, LOGIN_FAILED)

    auth.login(request, user)
    user.last_login = datetime.now()
    user.save()

    return WebAPIResponse(request)


@webapi
def account_logout(request, apitype="json"):
    auth.logout(request)
    return WebAPIResponse(request)
