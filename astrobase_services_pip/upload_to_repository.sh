#!/bin/bash
SOURCE="dist\astrobase_services-1.0.0.tar.gz"
DESTINATION="nvermaas@uilennest.net:~/www/repository"
curl --insecure --upload-file ${DESTINATION} -u upload:upload ${SOURCE}

# Next command will not close the window, can be handy if something goes wrong
#exec $SHELL