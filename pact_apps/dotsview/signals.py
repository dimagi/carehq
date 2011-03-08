from couchforms.signals import xform_saved
import logging
import simplejson

def process_dots_submission(sender, xform, **kwargs):

    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/dots_form":
            return
        try:
            dots_json = xform['xform']['case']['update']['dots']
            #update dots submission and parse the json data to be actually stored
            json_data = simplejson.loads(dots_json)
            xform['xform']['case']['update']['dots'] = json_data
            xform.save()
        except:
            logging.error("Error, dots submission did not have a dots block in the update section")
    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

