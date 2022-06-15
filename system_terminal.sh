#!/bin/bash

if [ -z $(docker ps -q --filter name=smartclinic-csti-1) ] 
then
    docker start -ai smartclinic-csti-1
else
    docker attach smartclinic-csti-1
fi
exit 0
