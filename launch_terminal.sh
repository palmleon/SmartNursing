#!/bin/bash


docker attach smartclinic-csti-1 --detach-keys=ctrl-t

#if [ -z $(docker ps -aq --filter name=csti) ] ; then
#    docker run --name csti -a=STDIN,STDOUT --link cdrsi:localhost --net smartclinic_default sti
#else 
#    docker start csti -ai
#fi
#echo "Quitting..."
#docker stop $(docker ps -aq --filter name=csti) &> /dev/null
