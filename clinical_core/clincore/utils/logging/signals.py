
"""
Use the django signals framework to handle exception logging.
"""

from django.dispatch import Signal

exception_logged = Signal(providing_args=["exc_info"])
