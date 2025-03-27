#!/bin/bash

# get location of this script
sourceDir=$BASH_SOURCE
runDir=$0
scriptsDir=$(cd $(dirname $sourceDir); pwd)

if [ ! $# -eq 1 ]; then
    echoc BRED "ERROR: You need to provide at least one argument."
    echoc BRED " The argument is the H1 PC (reemc-3c/reemc-3m) you want to deploy to."
    exit 1
fi

if [ ! "$1" == "reemc-3c" ] && [ ! "$1" == "reemc-3m" ]; then
    echoc BRED "ERROR: The argument is either 'reemc-3c' or 'reemc-3m'!"
	exit 1
fi

h1Pc=$1
h1Login=pal@$h1Pc
destDir=/home/pal/deployed_ws

src=install/
dest=$h1Login:$destDir

# remove src folder (install folder) to avoid copying old files
if [ -d $src ]; then
    echo "Remove install folder."
    rm -rf install
fi

# create install folder
catkin_make install
if [[ $? != 0 ]]; then
    exit 1
fi

# double check if we really want to deploy
echoc BYELLOW "Do you want to deploy to: " BBLUE "${h1Login} " BYELLOW "into the dir " BGREEN "${dest}" 
echo "Do you still want to deploy?"
select yn in "Yes" "No"; do
   case $yn in
       Yes ) break;;
       No ) echoc BLRED "The workspace was NOT deployed"; exit;;
   esac
done

# deploy
rsync --delete -avz $src $dest
if [[ $? != 0 ]]; then
    exit 1
fi

# additional info/notes
echoc BYELLOW "Deployment was successful."
echoc BYELLOW " NOTE: You need to source your workspace at the robot." 
