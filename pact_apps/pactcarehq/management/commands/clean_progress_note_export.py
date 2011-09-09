# django imports
from django.core.management.base import LabelCommand
from dimagi.utils.django.management import are_you_sure
from optparse import make_option
from couchforms.models import XFormInstance
from collections import defaultdict

class Command(LabelCommand):
    args = ''
    help = """
    A one time script run on September 9 to fix the format of export tags
    for all progress notes. 
    """
    
    option_list = LabelCommand.option_list + \
        (make_option('--dry-run', action='store_true', dest='dry_run', default=False,
            help='Only run this command as a dry-run, printing out what WOULD happen if you ran it for real.'),)

    
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run or are_you_sure("Run the export tag fixer? This will affect the LIVE database!"):
            print "getting forms"
            forms = XFormInstance.view("couchforms/by_xmlns", reduce=False,
                                       include_docs=True)
            found = len(forms)
            print "checking %s forms" % found
            changed = defaultdict(lambda: [0,0])
            
            for form in forms:
                if "#export_tag" in form:
                    tag = form["#export_tag"]
                    if isinstance(tag, list) and len(tag) == 1 and tag[0] == "xmlns":
                        form["#export_tag"] = "xmlns"
                        changed[form.xmlns][0] = changed[form.xmlns][0] + 1
                        if not dry_run:
                            form.save()
                changed[form.xmlns][1] = changed[form.xmlns][1] + 1
            
            for xmlns, counts in changed.items():
                print "Form %s changed %s of %s found forms" % (xmlns, counts[0], counts[1])
            
            

            