import os
import sys

netstat = os.popen('netstat -nlp')

fullcmd = netstat.read()
lines = fullcmd.split('\n')

runserver = ''
for line in lines:
    if line.count('127.0.0.1:8000') > 0 or line.count('0.0.0.0:8000') > 0:
        runserver=line
        print "found running instance"
        break
if runserver == '':
    print "cound not find open port"
    sys.exit()
splits = runserver.split(' ')

distilled = []

for item in splits:
    if item == '':
        continue
    else:
        distilled.append(item)

if distilled[-1].count('python') > 0:
    pid = distilled[-1].split('/')[0]
    killer = os.popen('kill ' + pid)
    killed = killer.read()
    print killed
    print "python task killed"
