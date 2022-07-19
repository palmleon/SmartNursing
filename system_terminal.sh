#!/bin/bash

if [ -z $(docker ps -q --filter name=smartnursing-csti-1) ] 
then
    docker start -ai smartnursing-csti-1
else
    docker attach smartnursing-csti-1
fi
exit 0
