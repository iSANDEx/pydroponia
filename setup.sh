#!/bin/bash

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

echo "Using the profile file: ${PROFILE}"

if [[ "${BIOAGROLOGPATH}" == "" ]]; then
    BIOAGROLOGPATH="${HOME}/bin/bioagro"
    echo "export BIOAGROLOGPATH=${BIOAGROLOGPATH}" >>"${HOME}/${PROFILE}"
    source "${HOME}/${PROFILE}"
    echo "Env variable BIOAGROLOGPATH(=${BIOAGROLOGPATH}) created"
else
    echo "BIOAGROLOGPATH(=${BIOAGROLOGPATH}) already exists"
    echo "Nothing done"
fi

if [[ "${AVRDUDE}" == "" ]]; then
    AVRDUDE="/usr/local/bin/arduino"
    echo "export AVRDUDE=${AVRDUDE}" >>"${HOME}/${PROFILE}"
    source "${HOME}/${PROFILE}"
    echo "Env variable AVRDUDE(=${AVRDUDE}) created"
else
    echo "AVRDUDE(=${AVRDUDE}) already exists"
    echo "Nothing done"
fi


if [ ! -d "${BIOAGROLOGPATH}" ]; then
    mkdir -p "${BIOAGROLOGPATH}"
    echo "Created (recursively) the folder ${BIOAGROLOGPATH}"
fi

if [[ "${PYDROPATH}" == "" ]]; then
    PYDROPATH="${BIOAGROLOGPATH}/pydroponia"
    echo "export PYDROPATH=${BIOAGROLOGPATH}/pydroponia" >>"${HOME}/${PROFILE}"
    source "${HOME}/${PROFILE}"
    echo "Env variable PYDROPATH(=${PYDROPATH}) created"
fi

echo "Replacing the content of 'pydroponia' into ${BIOAGROLOGPATH}"
rsync -a --delete ./ "${BIOAGROLOGPATH}"
#cp -r ./* "${BIOAGROLOGPATH}"

echo "Replacing Arduino libraries in ${HOME}/Arduino/libraries with the latest versions..."
rsync -a --delete ./arduino/libs/ "${HOME}/Arduino/libraries/"
#cp -r ./arduino/libs/* "${HOME}/Arduino/libraries/."

echo "****************************************************"
