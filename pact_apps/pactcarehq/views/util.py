DAYS_OF_WEEK = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

def ms_from_timedelta(td):
    """
    Given a timedelta object, returns a float representing milliseconds
    """
    return (td.seconds * 1000) + (td.microseconds / 1000.0)


form_xmlns_to_names = {
    'http://dev.commcarehq.org/pact/dots_form': "DOTS",
    'http://dev.commcarehq.org/pact/progress_note': "Progress Note",
    'http://dev.commcarehq.org/pact/bloodwork': "Bloodwork",
    'http://dev.commcarehq.org/pact/mileage': "Mileage",
    'http://dev.commcarehq.org/pact/patientupdate': "Patient Update",
}

