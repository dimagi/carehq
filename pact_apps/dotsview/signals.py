from couchforms.signals import xform_saved
import logging
from dotsview.formprocess import process_dots_json

def process_dots_submission(sender, form, **kwarsg):
    if form.xmlns != "http://dev.commcarehq.org/pact/dots_form":
        print "skipping non dots"
        return
    try:
        print "process_dots_submission triggered"
        dots_json = form['form']['case']['update']['dots']
        observations = process_dots_json(form, dots_json)
    except:
        logging.error("Error, dots submission did not have a dots block in the update section")
    pass

xform_saved.connect(process_dots_submission)

