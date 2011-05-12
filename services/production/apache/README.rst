carehq_static.conf
==================

Serve static content for carehq information.  This in simple configurations will be the same machine that the django code is running in a different process.
This is an apache config for the configuration.

proxy.conf
==========

Proxy information for the apache proxy instance in front of carehq and its static service.
Will proxy data via https to carehq's django port and static information as well.
