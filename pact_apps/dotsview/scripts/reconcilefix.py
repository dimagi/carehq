from dotsview.models.couchmodels import CObservation, CObservationAddendum, ADDENDUM_NOTE_STRING

def run():
    observations = CObservationAddendum.view('pactcarehq/dots_addendums', startkey=['addendum_group', 'created', '\x00'], endkey = ['addendum_group', 'created',u'\ufff0'], include_docs=True).all()
    for obs in observations:
        print obs
        #if it's off a document
        print obs['observed_date']
        for o in obs.art_observations:
            o.is_reconciliation=True
            if o.day_note == ADDENDUM_NOTE_STRING:
                o.day_note = ''
            #o.save()
        for o in obs.nonart_observations:
            o.is_reconciliation=True
            if o.day_note == ADDENDUM_NOTE_STRING:
                o.day_note = ''
            #o.save()
        #print len(obs.art_observations)
        #print len(obs.nonart_observations)

        #obs.is_reconciled=True
        obs.save()
