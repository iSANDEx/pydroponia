#!/usr/bin/env bash

# Created by Jose L. Ulloa, 2018
#
# Script to start the webserver:
# Starts the webserver and connect to the database:
if [[ "${OSTYPE}" == darwin* ]]; then
    # If Mac OS
    PROFILE='.bash_profile'
elif [[ "${OSTYPE}" == linux* ]]; then
    # If Linux
    PROFILE='.profile'
else
    # For now just say everything else uses .profile too
    PROFILE='.profile'
fi

echo "****************************************************"
echo $( date )
echo "Using the profile file: ${PROFILE}"
source "${HOME}/${PROFILE}"
sudo PYDROCONF="${HOME}/.pydroponia" PYDROPATH="${PYDROPATH}" ${PYDROPATH}/web_server/display_sensor_data.py &
