#!/bin/bash

if [ -z $(docker ps -q --filter name=crei) ] 
then
    docker start -ai smartclinic-crei-1
else
    docker attach smartclinic-crei-1
fi
exit 0
