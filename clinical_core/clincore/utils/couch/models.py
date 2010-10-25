from django.conf import settings
from couchdbkit.ext.django.schema import *
from distutils.version import LooseVersion

"""Shared models"""


class AppVersionedDocument(Document):
    """Mixin to add a version attribute and properties to a document in couch."""
    
    app_version = StringProperty()
    
    def requires_upgrade(self):
        """
        Whether this patient requires an upgrade, based on the app version number
        """
        # no version = upgrade fo sho
        if not self.app_version:
            return True
        return LooseVersion(self.app_version) < LooseVersion(settings.BHOMA_APP_VERSION)
        
    def save(self, *args, **kwargs):
        # override save to add the app version
        if not self.app_version:
            self.app_version = settings.BHOMA_APP_VERSION
        super(AppVersionedDocument, self).save(*args, **kwargs)
    
    class Meta:
        app_label = 'patient'

        