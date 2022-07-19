#!/bin/bash

if [ -z $(docker ps -q --filter name=SmartNursing-crei) ] 
then
    docker start -ai SmartNursing-crei-1
else
    docker attach SmartNursing-crei-1
fi
exit 0
