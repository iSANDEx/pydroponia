#!/usr/bin/env bash
# This script installs locally a copy of the repository and sets up the software for the first time.
# For any subsequent update, use the script update.sh

# 1. Creates the local directory where to store the source code:
PydroFldr="pydroponia"
VerFldr="version1.0"
PydroPath="${HOME}/${PydroFldr}/${VerFldr}"
if [ ! -d "${HOME}/${PydroFldr}" ]; then
    echo "${HOME}/${PydroFldr} folder does not exist. Creating one..."
else
    echo "${HOME}/${PydroFldr} already exists, backing it up and creating a new one..."
    mv "${HOME}/${PydroFldr}" "${HOME}/${PydroFldr}_Backup"
fi
mkdir -p "${PydroPath}"

echo "***************************************"
echo "Cloning repository, please wait..."
mkdir -p "${PydroPath}"
cd "${PydroPath}"

# 2. Downloads the source code into the directory
git clone git@bitbucket.org:jlulloa/pydroponia.git
echo "Repository cloned."
echo "***************************************"

# 3. Initial set up of Pydroponia
echo "Installing the software..."
cd "${PydroPath}/pydroponia"
./setup.sh

# 4. Create symbolic links in ${HOME}
cp "${PydroPath}/pydroponia/pydro_install.sh" "${HOME}"
ln -s "${HOME}/bin/bioagro/pydro_update.sh" "${HOME}/pydro_update.sh"

# 5. Finish installation
echo "To start up the software:"
echo " - Move to the directory ~/bin/bioagro"
echo " - Run the script ./start.sh"
echo "***************************************"

