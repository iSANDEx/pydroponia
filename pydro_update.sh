#!/usr/bin/env bash
# This script updates the local repository and updates the software.

# 1. Moves to the local repository:
PydroFldr="pydroponia"
VerFldr="version1.0"
PydroPath="${HOME}/${PydroFldr}/${VerFldr}/pydroponia"
echo "***************************************"
echo "Updating the repository, please wait..."
cd "${PydroPath}"
git pull
echo "Repository updated."
echo "***************************************"

# 2. Updating the software
echo "Updating the software..."
cd "${PydroPath}"
./setup.sh
echo "To start up the software:"
echo " - Move to the directory ~/bin/bioagro"
echo " - Run the script ./start.sh"
echo "***************************************"
