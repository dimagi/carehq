import socket
import uuid
from datetime import datetime, timedelta
import random

ZEBRA_SEND_TIMOUT=1500
ZEBRA_RECEIVE_TIMEOUT=1500

host = '192.168.0.85'
port = 9100

#command = "^XA^FO10,10,^AO,30,20^FDFDTesting^S^FO10,30^BY3^BCN,100,Y,N,N^FDTesting^FS^XZ"

#name, age, gender, oh yeah.
#^FO50,50^B3N,N,100,Y,N^FD123456^FS
#THIS IS THE QR CODE COMMAND
#QR code  BQ,2,[<zoom/scale> 5 or 6, maybe 4, but 6 is the max for the 2x1],Q|M, Q is default, 
#
command = """
^XA
^FO20,15^BQ,2,5,,^FDMA,%(barcode_data)s^FS
^FO175,20^A0,30,22^FD%(last_name)s,^FS
^FO175,50^A0,24,^FD%(first_name)s^FS
^FO175,100^ABN,16,^FDSex: %(gender)s Age: %(age)s^FS
^FO175,120^ABN,16,^FDID: %(external_id)s^FS
^FO175,140^ABN,16,^FDAdmit Date: %(enroll_date)s^FS
^PQ3,,,,
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

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))


def qr_code():
    label_data = {}
    label_data['barcode_data']=uuid.uuid1().hex
    label_data['last_name']='Jackson'
    label_data['first_name']='Jonathan'
    label_data['gender']='M'
    label_data['age']='29'
    label_data['external_id']=random.randint(10000,99999)
    label_data['enroll_date']= (datetime.utcnow() - timedelta(days=random.randint(1,500))).strftime('%m/%d/%Y')
    s.send(command % (label_data))
    s.close()

def flat_code():
    label_data = {}
    #label_data['barcode_data']=uuid.uuid4().hex
    print label_data['barcode_data']
    label_data['last_name']='Jackson'
    label_data['first_name']='Jonathan'
    s.send(lab_command % (label_data))
    s.close()
flat_code()


