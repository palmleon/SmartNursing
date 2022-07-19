#!/bin/bash

if [ -z $(docker ps -q --filter name=SmartNursing-csti-1) ] 
then
    docker start -ai SmartNursing-csti-1
else
    docker attach SmartNursing-csti-1
fi
exit 0
