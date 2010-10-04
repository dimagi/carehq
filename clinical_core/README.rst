Dimagi Clinical Core Suite
==========================

This project consists of a suite of django apps that tightly integrate to form a basic patient/case management system for clinical applications.

The apps are extensible with the optional integration of couchdb to add additional data to patient and provider objects for the system.

A permissions framework is included to create granular access for patient management via the actors app.

actors
======

Permission framework for granting access and creating groups of caregivers and providers for patients

casetracker
===========

An app that allows providers and patients and caregivers to mange cases in the system that require human interpretation, documentation and action.

patient
=======

The app to manage the patient itself.  It is fully featured in django.  To extend it, you may use couchdbkit to append more metadata.


clincore
========

A wrapper module to centrally integrate these apps. 