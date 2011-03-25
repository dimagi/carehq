from mongoengine import Document as MongoDocument
from mongoengine import connect as MongoConnect
from mongoengine import StringField
from xml.etree.ElementTree import ElementTree
from django.utils.datastructures import SortedDict
import couchforms.const as const

from couchforms.models import XFormInstance, Metadata
from couchforms.safe_index import safe_index


class MongoXform(MongoDocument):
    """An XForms instance."""
    xmlns = StringField()

#    @property
#    def get_form(self):
#        """public getter for the xform's form instance, it's redundant with _form but wrapping that access gives future audit capabilities"""
#        return self._form
#
#    @property
#    def _form(self):
#        return self[const.TAG_FORM]
#
#    @property
#    def type(self):
#        return self._form.get(const.TAG_TYPE, "")
#
#    @property
#    def version(self):
#        return self._form.get(const.TAG_VERSION, "")
#
#    @property
#    def uiversion(self):
#        return self._form.get(const.TAG_UIVERSION, "")
#
#    @property
#    def metadata(self):
#        if (const.TAG_META) in self._form:
#            meta_block = self._form[const.TAG_META]
#            meta = Metadata(meta_block)
#            return meta
#
#        return None
#
#    def __unicode__(self):
#        return "%s (%s)" % (self.type, self.xmlns)
#
#    def xpath(self, path):
#        """
#        Evaluates an xpath expression like: path/to/node and returns the value
#        of that element, or None if there is no value.
#        """
#        return safe_index(self, path.split("/"))
#
#
#    def found_in_multiselect_node(self, xpath, option):
#        """
#        Whether a particular value was found in a multiselect node, referenced
#        by path.
#        """
#        node = self.xpath(xpath)
#        return node and option in node.split(" ")
#
#
#    def top_level_tags(self):
#        """
#        Get the top level tags found in the xml, in the order they are found.
#        """
#        xml_payload = self.get_xml()
#        element = ElementTree.XML(xml_payload)
#        to_return = SortedDict()
#        for child in element:
#            # fix {namespace}tag format forced by ElementTree in certain cases (eg, <reg> instead of <n0:reg>)
#            key = child.tag.split('}')[1] if child.tag.startswith("{") else child.tag
#            to_return[key] = self.xpath('form/' + key)
#        return to_return



def run():
    all_xforms = XFormInstance.view('pactcarehq/all_submits', include_docs=True, limit=100).all()
    total = XFormInstance.view('pactcarehq/all_submits').count()
    MongoConnect('pact_test')
    for idx, f in enumerate(all_xforms):
        print "Saving form %s to mongo: %d/%d" % (f._id, idx, total)
        json = f.to_json()
        #json['id'] = json['_id']
        mx = MongoXform(**json)
        mx.save()



