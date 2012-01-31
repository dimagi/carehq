from couchforms.models import XFormInstance
import hashlib

def run():
    dupes = {}
    docs = XFormInstance.view('couchforms/by_xmlns', key='urn:hl7-org:v3', include_docs=True, reduce=False).all()
    for doc in docs:
        attachment = doc.fetch_attachment('form.xml')
        checksum = hashlib.md5(attachment).hexdigest()


        filebuilder = ['ccd']
        filebuilder.append(doc.received_on.strftime("%Y-%m-%d-%H%M"))
        if dupes.has_key(checksum):
            dupes[checksum] += 1
            filebuilder.append('%s_%d' % (checksum, dupes[checksum]))
        else:
            dupes[checksum] = 0
            filebuilder.append(checksum)
        filebuilder.append(doc._id)
        filename = '_'.join(filebuilder) + '.xml'
        fout = open(filename, 'w')
        fout.write(attachment)
        fout.close()

