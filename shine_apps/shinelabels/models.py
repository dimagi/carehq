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

    class Meta:
        verbose_name = "Zebra Printer"
        verbose_name_plural = "Zebra Printers"

    def __unicode__(self):
        return "%s (%s@%s)" % (self.name, self.location, self.ip_address)

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
    fulfilled_date = models.DateTimeField(blank=True, null=True)

    zpl_code=models.TextField()

    class Meta:
        verbose_name = "Label Print Queue"
        verbose_name_plural = "Label Print Jobs"


    @property
    def get_printer(self):
        return self.destination.id

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

    #Custom:
    #heartbeat True (reachable) false (unreachable)

    printer = models.ForeignKey(ZebraPrinter, related_name='status_history')
    event_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=32, db_index=True)
    is_cleared = models.BooleanField(default=False, help_text="If there is something set on the machine, then that indicates a problem.  If the printer sets it 'cleared', this is true.  So True=OK, False=Bad, with the exception of successful print jobs, they set to false")

    class Meta:
        verbose_name = "Zebra Printer Status"
        verbose_name_plural = "Printer Statuses"

    def __unicode__(self):
        return "(%s) %s %s" % (self.event_date.strftime("%m/%d/%Y"), self.status, self.is_cleared)

from signals import *
