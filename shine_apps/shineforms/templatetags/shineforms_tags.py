from django import template


from datetime import datetime, date
import types
from django.template.context import Context
from shineforms.lab_utils import merge_labs
from couchforms.models import XFormInstance

from couchforms.templatetags import xform_tags
from shineforms.constants import xmlns_display_map, STR_MEPI_ENROLLMENT_FORM, STR_MEPI_CLINICAL_QUEST_FORM, STR_MEPI_OUTCOME_FORM, STR_MEPI_LAB_FOUR_FORM, STR_MEPI_LAB_THREE_FORM, STR_MEPI_LAB_TWO_FORM, STR_MEPI_LAB_ONE_FORM, STR_MEPI_LABDATA_FORM, STR_MEPI_FOLLOWUP_FORM

register = template.Library()

def format_name(value):
    if not isinstance(value, basestring):
        value = unicode(value)
    return value.replace("_", " ")

def render_base_type(key, value):
    if not value:
        return "<tr><td><span class='prompt'>%s</span></td><td></td></tr>" % format_name(key)
    return "<tr><td><span class='prompt'>%s</span></td><td><span class='value'>%s</span></td></tr>" % (format_name(key), format_name(value))

def is_base_type(value):
    return isinstance(value, basestring) or \
           isinstance(value, date) or \
           isinstance(value, datetime)


@register.simple_tag()
def render_form(form):
    ret = []
    for k, v in form.items():
        ret.append(render_kv(k,v))

    return "<table>%s</table>" % (''.join(ret))

def is_hidden_field(field_key):
    # hackity hack this static list of things we don't actually
    # want to display
    SYSTEM_FIELD_NAMES = ("drugs_prescribed", "case", "meta", "clinic_ids", "drug_drill_down", "tmp", "info_hack_done")
    return field_key.startswith("#") or field_key.startswith("@") or field_key.startswith("_") \
           or field_key.lower() in SYSTEM_FIELD_NAMES

def render_kv(nodekey, nodevalue):
    if not nodevalue or is_hidden_field(nodekey): return ""
    if is_base_type(nodevalue):
        return render_base_type(nodekey, nodevalue)

    header = format_name(nodekey)

    if isinstance(nodevalue, types.DictionaryType):
        node_list = []
        for key, value in nodevalue.items() :
            # recursive call
            node = render_kv(key, value)
            if node: node_list.append(node)

        if node_list:
            return "<tr><td><span class='prompt'>%(header)s</span></td><td><table>%(body)s</table></td></tr>" % \
                    {"header": header,
                     "body": "".join(node_list)}
        else:
            return ""
    elif isinstance(nodevalue, types.ListType) or  isinstance(nodevalue, types.TupleType):
        full_list = []
        for item in nodevalue:
            node_list = []
            if is_base_type(item):
                node_list.append("<li>%s</li>" % format_name(item))
            elif isinstance(item, types.DictionaryType):
                for key, value in item.items():
                    node = render_kv(key, value)
                    if node:
                        node_list.append(node)
            else:
                node_list.append("<li>%s</li>" % format_name(str(item)))
        full_list.append("<tr><td><span class='prompt'>%(header)s</span></td><td><ul>%(body)s</ul></td></tr>" % \
                             {"header": header,
                              "body": "".join(node_list)})
    else:
        return render_base_type(nodekey, nodevalue)

@register.simple_tag
def shine_xmlns_name(xmlns):
    return xmlns_display_map.get(xmlns, 'Unknown')


@register.simple_tag
def render_submission_fragment(xmlns, submissions):
    """

    """
    template_name = 'shineforms/generic_fragment.html'
    context = {}
    if xmlns == STR_MEPI_ENROLLMENT_FORM:
#        template_name = 'shineforms/enrollment_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns ==  STR_MEPI_CLINICAL_QUEST_FORM:
#        template_name = 'shineforms/clinical_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns == STR_MEPI_FOLLOWUP_FORM:
#        context = {template_name = 'shineforms/followup_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns == STR_MEPI_LABDATA_FORM:
        template_name = 'shineforms/labdata_fragment.html'
        context = {'labs': merge_labs(submissions, as_dict=True)}
    elif xmlns == STR_MEPI_LAB_ONE_FORM:
        context = {'submission': submissions[0]}
#        template_name = 'shineforms/lab_one_fragment.html'
    elif xmlns == STR_MEPI_LAB_TWO_FORM:
#        template_name = 'shineforms/lab_two_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns == STR_MEPI_LAB_THREE_FORM:
#        template_name = 'shineforms/lab_three_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns == STR_MEPI_LAB_FOUR_FORM:
#        template_name = 'shineforms/lab_four_fragment.html'
        context = {'submission': submissions[0]}
    elif xmlns == STR_MEPI_OUTCOME_FORM:
#        template_name = 'shineforms/outcome_fragment.html'
        context = {'submission': submissions[0]}
    t = template.loader.get_template(template_name)
    return t.render(Context(context, autoescape='on'))



@register.simple_tag
def get_status_matrix(patient):

    context_dict = dict()
    tally = patient.get_completed_tally
    for tup in tally:
        #(displayname, (True|False, instance))
        displayname = tup[0]
        status = tup[1][0]
        instance = tup[1][1]
        if displayname == "Enrollment":
            context_dict['enrollment'] = status
        elif displayname == "Clinical Info":
            context_dict['clinical_info'] = status
        elif displayname == "Lab Data":
            submissions = patient._get_case_submissions(patient.latest_case)
            lab_submissions = filter(lambda x: x.xmlns == STR_MEPI_LABDATA_FORM, submissions)
            labs_dict = merge_labs(lab_submissions, as_dict=True)
            for k,v in labs_dict.items():
                lab_status=False
                if isinstance(v, str) or isinstance(v, unicode):
                    if v == '':
                        lab_status = False
                    else:
                        lab_status=True

                elif isinstance(v, dict):
                    lab_status = v
                context_dict['lab_%s' % k] = lab_status
        elif displayname == "Emergency Lab":
            #do check on positivity
            if status:
                bottles = patient.get_elab_bottle_data
                if len(bottles) > 0:
                    context_dict['emergency_lab'] = True
                    context_dict['is_positive'] = True
                else:
                    context_dict['emergency_lab'] = True
                    context_dict['is_positive'] = False

            else:
                context_dict['emergency_lab'] = False
                context_dict['is_positive'] = False

        elif displayname == "Biochemical Lab":
            context_dict['biochemical']=status
        elif displayname == "Speciation":
            context_dict['speciation']=status
        elif displayname == "Sensitivity":
            context_dict['sensitivity']=status
        elif displayname == "Outcome" or displayname == "Old Follow Up/Outcome":
            context_dict['outcome']=status

    t = template.loader.get_template('shineforms/status_matrix.html')


    return t.render(Context(context_dict, autoescape=False))
