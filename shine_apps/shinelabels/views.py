from shinelabels.models import ZebraPrinter

def printer_status(request, template="shinelabels/printer_status.html"):
    printers = ZebraPrinter.objects.all()


def print_jobs(request, template="shinelabels/printer_jobs.html"):
    """
    Display outstanding jobs for the printer
    """


    if request.method == "POST":
        #submit a new print job
        #request.POST.get('printer_id')
        #request.POST.get('case_id')
        #generate a new print job, generate ZPL, and make a new LabelQueue

        pass
    pass




