from shinelabels.models import ZebraStatus

def condense_status_logs():
    """
    Helper function to clean up logs in the zebra label queue
    """

    #algorithm:
    #for each status event.
    states = ZebraStatus.objects.all().order_by('-event_date')
    total_states = states.count()

    deletes = []


    for i, state in enumerate(states):
        if i == total_states - 1:
            break
        next_state = states[i+1]

        if state.printer == next_state.printer and state.status == next_state.status and state.is_cleared == next_state.is_cleared:
            #everything is the same, delete next
            next_state.delete()
        else:
            continue
