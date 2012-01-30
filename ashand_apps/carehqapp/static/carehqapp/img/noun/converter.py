import os
import sys
import subprocess
#print sys.argv
#rsvg-convert -w 75 -a noun_care_staff.svg -o noun_care_staff_75.png^C


filename = sys.argv[1]
size = sys.argv[2]

outfile = "%s_%s.png" % (filename.split('.')[0], size)

print subprocess.call(["rsvg-convert", "-w", size, '-a', filename, '-o', outfile])
