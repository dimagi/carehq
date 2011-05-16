Dimagi Patient Core Library
===========================

The purpose of the patient library is to provide basic views and functionality for creating applications that deal with patients and permissions.

The framework provides hooks into our actor system, but the actual implementation and domain specific use cases need to be left up to you the implementor.

Subclass BasePatient, the default couchviews will be useful, but you should make specific view files for your implementaion.

URLs and django views for interacting and manipulating your models should also be done within your own application.