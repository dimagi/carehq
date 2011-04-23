from couchforms.signals import xform_saved
import logging
import simplejson

def process_dots_submission(sender, xform, **kwargs):

    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/dots_form":
            return
        try:
            dots_json = xform['form']['case']['update']['dots']
            #update dots submission and parse the json data to be actually stored
            if isinstance(dots_json, str) or isinstance(dots_json, unicode):
                json_data = simplejson.loads(dots_json)
                xform['form']['case']['update']['dots'] = json_data
                xform.save()
        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))


        if isinstance(xform['form']['pillbox_check'], str):
            return

        if isinstance(xform['form']['pillbox_check'], unicode):
            return

        if not xform['form']['pillbox_check'].has_key('check'):
            return

        pillbox_check_str = xform['form']['pillbox_check']['check']
        if isinstance(pillbox_check_str, dict):
            #print "dictionary, skipping"
            return
        elif isinstance(pillbox_check_str, str) or isinstance(pillbox_check_str, unicode):
            json_data = simplejson.loads(pillbox_check_str)
            xform['form']['pillbox_check']['check'] = json_data


            str1 = simplejson.dumps(json_data)
            str2 = simplejson.dumps(xform['form']['case']['update']['dots'])
            xform.save()

    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

