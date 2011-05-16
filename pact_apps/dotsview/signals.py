from couchforms.signals import xform_saved
import logging
import simplejson

def process_dots_submission(sender, xform, **kwargs):

    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/dots_form":
            return
        try:
            dots_json = xform['form']['case']['update']['dots']
            if isinstance(dots_json, str) or isinstance(dots_json, unicode):
                json_data = simplejson.loads(dots_json)
                xform['pact_data'] = {}
                xform['pact_data']['dots'] = json_data
                xform.save()
        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

