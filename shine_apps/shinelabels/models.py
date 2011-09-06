from django.db import models


class ZebraPrinter(models.Model):
    LOCATION_CHOICES=(
        ('lab_urgencia', 'Laboratory Urgencia'),
        ('lab_central', 'Central Lab'),
        ('medicine_ward', 'Medicine Ward'), #may need to be redefined later
    )
    ip_address = models.IPAddressField()
    name = models.CharField(max_length=128, null=True, blank=True) #may or may not be hostname
    port = models.PositiveIntegerField()

    location = models.CharField(max_length=64, choices=LOCATION_CHOICES)

    serial_number = models.CharField(max_length=32)
    mac_address = models.CharField(max_length=32)

class LabelQueue(models.Model):
    """
    The LabelQueue is a model for a REST api for the printer queue processor on the netbook in the lab to process and eventually marshall out
    print jobs to the printers using host information defined.

    Separate logic will be necessary to generate the ZPL code and choose the ultimate destination.

    fulfilled_date is contingent upon a successful job, the service will recall this ID, set the fulfilled date and resave.
    when fulfilled date is null, this is how the queue is picked up
    """
    case_guid = models.CharField(max_length=32)
    destination = models.ForeignKey(ZebraPrinter)

    created_date = models.DateTimeField()
    xform_id = models.CharField(max_length=32, help_text="XForm Submission that triggered this submission")
    fulfilled_date = models.DateTimeField()

    zpl_code=models.TextField()

class ZebraStatus(models.Model):
#    Accepted Values:
#    A = paper out
#    B = ribbon out
#    C = printhead over-temp
#    D = printhead under-temp
#    E = head open
#    F = power supply over-temp
#    G = ribbon-in warning (Direct Thermal Mode)
#    H = rewind full
#    I = cut error
#    J = printer paused
#    K = PQ job completed
#    L = label ready
#    M = head element out
#    P = power on
#    Q = clean printhead
#    R = media low
#    S = ribbon low
#    T = replace head
#    U = battery low
#    V = all errors

    #unreachable by client
#
    ZEBRA_STATUS=(
        ("paper_out","paper out"),
        ("ribbon_out","ribbon out"),
        ("printhead_overtemp","printhead over-temp"),
        ("printhead_undertemp","printhead under-temp"),
        ("head_open","head open"),
        ("power_supply_overtemp", "power supply over-temp"),
        ("ribbon-in_warning_dtm","ribbon-in warning (Direct Thermal Mode)"),
        ("rewind_full","rewind full"),
        ("cut_error","cut error"),
        ("printer_paused","printer paused"),
        ("PQ_job_completed","PQ job completed"),
        ("label_ready","label ready"),
        ("head_element_out","head element out"),
        ("power_on","power on"),
        ("clean_printhead","clean printhead"),
        ("media_low","media low"),
        ("ribbon_low","ribbon low"),
        ("replace_head","replace head"),
        ("battery_low","battery low"),
        ("all_errors","all errors"),

            #this is a custom error
        ('unreachable', 'Unreachable from printserver'),
    )
    printer = models.ForeignKey(ZebraPrinter)
    event_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=32, choices=ZEBRA_STATUS, db_index=True)
    is_triggered = models.BooleanField(default=False, help_text="If there is something set on the machine, then that indicates a problem.  If the printer sets it 'cleared', then that negates it")


    @classmethod
    def parse_message(cls, msg_text):
        pass

    def save(self, *args, **kwargs):
        pass





