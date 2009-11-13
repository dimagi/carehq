#
# errors.py -- Error classes and codes for webapi
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


class WebAPIError:
    """
    An API error, containing an error code and human readable message.
    """
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


#
# Standard error messages
#
NO_ERROR                  = WebAPIError(0,   "If you see this, yell at " +
                                             "the developers")
SERVICE_NOT_CONFIGURED    = WebAPIError(1,   "The web service has not yet "
                                             "been configured")

DOES_NOT_EXIST            = WebAPIError(100, "Object does not exist")
PERMISSION_DENIED         = WebAPIError(101, "You don't have permission " +
                                             "for this")
INVALID_ATTRIBUTE         = WebAPIError(102, "Invalid attribute")
NOT_LOGGED_IN             = WebAPIError(103, "You are not logged in")
LOGIN_FAILED              = WebAPIError(104, "The username or password was " +
                                             "not correct")
INVALID_FORM_DATA         = WebAPIError(105, "One or more fields had errors")
MISSING_ATTRIBUTE         = WebAPIError(106, "Missing value for the attribute")
