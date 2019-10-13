#!/bin/bash

##---------------------------------------------------------------------------------------------------------------------#
##! \brief   Description: This script uploads the created atdb_services artifact to the Nexus repository
##!          In:  $1   [Optional] Additional Artifact version tag which can be anything
##!          Out: None
##!          Returns: None
##!          Preconditions:
##!             - build should be done /dist/atdb_services-[version].tar.gz is available
##!          Postconditions:
##!             - artifact uploaded to https://support.astron.nl/nexus/content/repositories/snapshots/nl/astron/atdb/ATDB_services-[version][additional version tag].tar.gz
##!          Examples:     .\upload_to_nexus
##!                        .\upload_to_nexus 20180913
##!                        .\upload_to_nexus test
##---------------------------------------------------------------------------------------------------------------------#

VERSION=$(python setup.py --version)
ARTIFACT_NAME="ATDB_services"
ARTIFACT_BUILD="/dist/atdb_services-${VERSION}.tar.gz"

ARTIFACT_UPLOAD_BASE_PATH="https://support.astron.nl/nexus/content/repositories/snapshots/nl/astron/atdb/"
if [[ $# -eq 1 ]]; then
    ARTIFACT_VERSION="-${VERSION}-${1}"
else
    ARTIFACT_VERSION="-${VERSION}"
fi

ARTIFACT_UPLOAD_PATH="${ARTIFACT_UPLOAD_BASE_PATH}${ARTIFACT_NAME}${ARTIFACT_VERSION}.tar.gz"
ARTIFACT_BUILD_PATH="$(pwd)${ARTIFACT_BUILD}"

echo "Upload ${ARTIFACT_BUILD_PATH} to $ARTIFACT_UPLOAD_PATH"
curl --insecure --upload-file ${ARTIFACT_BUILD_PATH} -u upload:upload ${ARTIFACT_UPLOAD_PATH}

# Next command will not close the window, can be handy if something goes wrong
#exec $SHELL