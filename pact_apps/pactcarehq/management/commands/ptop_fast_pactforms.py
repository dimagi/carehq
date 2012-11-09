import logging
from django.core.mail import send_mail
from django.core.management.base import  BaseCommand
from couchforms.models import XFormInstance
from pactcarehq.pillows import PactFormsPillow

CHUNK_SIZE=500
POOL_SIZE = 15




class Command(BaseCommand):
    help = "Fast reindex of case elastic index by using the case view and reindexing cases"

    def handle(self, *args, **options):
#        confirm = raw_input("""
#    You have requested to do a case elastic index reset via fast track.
#    This will IRREVERSIBLY REMOVE
#    ALL index data in the case index and will take a while to reload.
#    Are you sure you want to do this. Also you MUST have run_ptop disabled for this to run.
#
#    Type 'yes' to continue, or 'no' to cancel: """)

#        if confirm != 'yes':
#            print "Reset cancelled."
#            return
#
#        confirm_ptop = raw_input("""Are you sure you disabled run_ptop? """)
#        if confirm_ptop != "yes":
#            return
#
#        confirm_alias = raw_input("""Are you sure you are not blowing away a production index?""")
#        if confirm_alias != "yes":
#            return


        #delete the existing index.
        pillow = PactFormsPillow()
        print "Deleting index"
        pillow.delete_index()
        print "Recreating index"
        pillow.create_index()
        print "Resetting CasePillow Checkpoint"
        pillow.reset_checkpoint()

        db = XFormInstance.get_db()
        start_num = 0

        print "starting fast tracked reindexing"
        chunk = db.view('couchforms/by_xmlns', reduce=False, key='http://dev.commcarehq.org/pact/dots_form', limit=CHUNK_SIZE, skip=start_num)

        #though this might cause some superfluous reindexes of docs,
        # we're going to set the checkpoint BEFORE we start our operation so that any changes
        # that happen to cases while we're doing our reindexing would not get skipped once we
        # finish.
        pillow.set_checkpoint({ 'seq': pillow.couch_db.info()['update_seq'] } )
        def do_index(item):
            print "Processing: %s" % item['id']
            pillow.processor(item, do_set_checkpoint=False)

        try:
            while len(chunk) > 0:
                for item in chunk:
                    pillow.processor(item, do_set_checkpoint=False)
                start_num += CHUNK_SIZE
                print "Grabbing next chunk: %d" % start_num
                chunk = db.view('couchforms/by_xmlns', reduce=False, key='http://dev.commcarehq.org/pact/dots_form', limit=CHUNK_SIZE, skip=start_num)

            print "Index recreated - you may now restart run_ptop"
#            send_mail('[commcare-hq] Pillowtop Case Reindex Complete', "Case reindex complete for index %s - it may now be aliased to hqcases" % pillow .es_index, 'hq-noreply@dimagi.com', ['commcarehq-dev@dimagi.com'], fail_silently=True)
        except Exception, ex:
            logging.exception("Case pillowtop fast reindex failed: %s" % ex)

