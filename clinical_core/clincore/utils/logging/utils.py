from __future__ import absolute_import
import logging
import sys
import traceback
from bhoma.utils.logging.signals import exception_logged


LOG_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}

def get_log_level(level):
    return LOG_LEVELS.get(level, logging.INFO)
    
def set_log_level(level):
    loglevel = LOG_LEVELS.get(level, logging.INFO)
    logging.basicConfig(level=loglevel)
    
def log_exception(e=None, extra_info=""):
    """Log an exception, with a stacktrace"""
    # you don't actually need the exception, since we rely on exc_info
    # left as an optional param because of existing code calling it
    # todo: do something smarter with extra info
    if extra_info: 
        logging.error(extra_info)
    exc_type, value, tb = sys.exc_info()
    if e is not None:
        # if they passed in an exception use it.  this should be always
        # the same, otherwise the stack trace will be wrong.
        value = e
        exc_type = type(e)
    traceback_string = "".join(traceback.format_tb(tb))
    logging.error("%s: %s" % (exc_type, value))
    logging.error(traceback_string)
    exception_logged.send(sender="logutil", exc_info=(exc_type, value, tb), extra_info=extra_info)
