from couchforms.signals import xform_saved
import logging
import simplejson

def process_dots_submission(sender, form, **kwargs):
    if form.xmlns != "http://dev.commcarehq.org/pact/dots_form":
        print "skipping non dots"
        return
    try:
        print "process_dots_submission triggered"
        dots_json = form['form']['case']['update']['dots']
        #observations = process_dots_json(form, dots_json) # deprecating this, we no longer store in django model, but use a view
        
        
        
        
        
        #update dots submission and parse the json data to be actually stored
        json_data = simplejson.loads(dots_json)
        form['form']['case']['update']['dots'] = json_data
        form.save()

    except:
        logging.error("Error, dots submission did not have a dots block in the update section")
    pass

xform_saved.connect(process_dots_submission)

