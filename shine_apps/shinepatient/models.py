from patient.models.patientmodels import BasePatient


class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    def is_unique(self):
        return True

    @property
    def view_name(self):
        return "shine_single_patient"