#!/bin/bash

cd Terminal

if [ -z $(docker ps -aq --filter name=csti) ] ; then
    docker run --name csti -it --link cdrsi:localhost --net smartclinic_default sti
else 
    docker start csti -ai
fi
echo "Quitting..."
docker stop $(docker ps -aq --filter name=csti) &> /dev/null
