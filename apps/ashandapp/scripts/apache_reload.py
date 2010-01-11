#really simple script to reload apache for the build server environment.

import os
import logging
runCmd = "sudo /etc/init.d/apache2 restart"
try:
    os.system(runCmd)
except:
    logging.error("Error reloading apache")
