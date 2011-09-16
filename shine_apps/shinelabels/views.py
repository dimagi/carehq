


def printer_status(request, template="shinelabels/printer_status.html"):
    printers = ZebraPrinter.objects.all()



