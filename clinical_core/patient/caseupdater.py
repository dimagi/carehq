


class CasePropertyWrapper(object):
    """
    Base class for making simple "transactional" updates for specific parts of the patient object. As well as providing
    simple wrapper for complex case concepts. (phone, address lists)
    """

    xml_template = None
    case=None

    def __init__(case):
        self.case=case

    #Implementer needs to create setters and getters


    def get_update_xml(self):
        """
        Method to create submission xml for said properties.
        """
        pass


