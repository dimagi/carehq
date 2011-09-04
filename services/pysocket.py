import socket
import uuid
from datetime import datetime, timedelta
import random

ZEBRA_SEND_TIMOUT=1500
ZEBRA_RECEIVE_TIMEOUT=1500

host = '192.168.1.8'
port = 9100

#command = "^XA^FO10,10,^AO,30,20^FDFDTesting^S^FO10,30^BY3^BCN,100,Y,N,N^FDTesting^FS^XZ"

#name, age, gender, oh yeah.
#^FO50,50^B3N,N,100,Y,N^FD123456^FS
#THIS IS THE QR CODE COMMAND
#QR code  BQ,2,[<zoom/scale> 5 or 6, maybe 4, but 6 is the max for the 2x1],Q|M, Q is default, 
#
qr_command = """
^XA
^FO20,15^BQ,2,5,,^FDMA,%(barcode_data)s^FS
^FO175,20^A0,30,22^FD%(last_name)s,^FS
^FO175,50^A0,24,^FD%(first_name)s^FS
^FO175,100^ABN,16,^FDSex: %(gender)s Age: %(age)s^FS
^FO175,120^ABN,16,^FDID: %(external_id)s^FS
^FO175,140^ABN,16,^FDAdmit Date: %(enroll_date)s^FS
^XZ
"""

lab_command = """
^XA
^FO20,15^A0,24,^FD%(last_name)s, %(first_name)s^FS
^FO20,45
^BY3^BCN,100,Y,N,N
^FD>;%(barcode_data)s^FS
^XZ
"""

#max_len=21 for surname
#max_len=21 for firstname
#save this to the printer as an image for dispaly. SAVES PAPER
#^ISR:EXERPROG.GRF,N

#print quantity of 3
# ^PQ3,,,, 


#sets print width in dots (203dpi)
#^PW406

#as a control command, we can send it this way too:
#^XA^PW406^XZ
#^XA^JUS^XZ
#The ^JUS command saves the value in memory and is optional in the application.

def do_send(zpl_string): #destination
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((host,port))
        s.send(zpl_string)
    except Exception, ex:
        print "*** Error sending: %s" % (ex)


    try:
        #print s.recv(1024)
        pass
    except Exception, ex:
        print "**** Error trying to read from socket %s" % ex

    try:
        s.close()
    except Exception, ex:
        print "*** Error trying to clos socket %s" % ex

def qr_code():
    label_data = {}
    label_data['barcode_data']=uuid.uuid4().hex
    label_data['last_name']='Preziosi'
    label_data['first_name']='Mike'
    label_data['gender']='M'
    label_data['age']='999'
    label_data['external_id']=random.randint(10000,99999)
    label_data['enroll_date']= (datetime.utcnow() - timedelta(days=random.randint(1,500))).strftime('%m/%d/%Y')
    do_send(qr_command % (label_data))

def flat_code():
    label_data = {}
    label_data['barcode_data']="I REALLY RULE!!!"#uuid.uuid4().hex
    #print label_data['barcode_data']
    label_data['last_name']='Preziosi'
    label_data['first_name']='Mike'
    do_send(lab_command % (label_data))
qr_code()


