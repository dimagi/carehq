from django import template
from couchdbkit.schema.properties import LazyDict
import string

register = template.Library()

@register.simple_tag
def get_table_from_json(json_object):
    return _render_json(json_object, root=True)

def _render_json(json_object, root=False):
    retstring = "<table>"
    if root:
       retstring += """<thead> <tr> <th>Field</th> <th>Value</th> </tr> </thead>"""
       retstring += "<tbody>"

    for key, val in json_object.items():
        retstring += "<tr>"
        retstring += "<td>%s</td>" % (string.capwords(key.replace('_', ' '), ' '))
        if isinstance(val, LazyDict) or isinstance(val, dict):
            ##if it's another dictionary, recurse and render a table in the cell
            retstring += "<td>%s</td>" % (_render_json(val, root=False))
        elif isinstance(val, list):
            #if it's a list, render it line by line, or recurse into each item
            retstring += "<td>"
            for item in val:
                if isinstance(item, LazyDict) or isinstance(item, dict):
                    retstring += "%s" % (_render_json(item, root=False))
                else:
                    retstring += "%s<br>" % (item)
            retstring += "</td>"
        elif isinstance(val, str) or isinstance(val, unicode):
            retstring += "<td>%s</td>" % (val.title())
        else:
            retstring += "<td>%s</td>" % (val)
        retstring += "</tr>"
    if root:
        retstring += "</tbody>"
    retstring += "</table>"
    return retstring
