

class TypedSubclassMixin(object):
    _subclass_dict = {}
    @classmethod
    def _get_subclass_dict(cls):
        if len(cls._subclass_dict.keys()) == 0:
            for c in cls.__subclasses__():
                cls._subclass_dict[unicode(c.__name__)] = c
        return cls._subclass_dict


    @classmethod
    def get_typed_from_dict(cls, doc_dict):
        doc_type = doc_dict['doc_type']
        if cls._get_subclass_dict().has_key(doc_type):
            cast_class = cls._get_subclass_dict()[doc_type]
        else:
            cast_class = BasePatient
            logging.error("Warning, unable to retrieve and cast the stored doc_type of the patient model.")
        return cast_class.wrap(doc_dict)

    @classmethod
    def get_typed_from_id(cls, doc_id):
        """
        Using the doc's stored doc_type, cast the retrieved document to the requisite couch model
        """
        #todo this is hacky in a multitenant environment
        db = cls.get_db()
        doc_dict = db.open_doc(doc_id)
        return cls.get_typed_from_dict(doc_dict)