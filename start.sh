#!/bin/bash
# Created by Jose L. Ulloa, 2018
#
# Script to run in normal operation
# Execute the python script pydroponia.py:

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
python3  "${PYDROPATH}/pydroponia.py" &
