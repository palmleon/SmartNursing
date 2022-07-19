#!/bin/bash

if [ -z $(docker ps -q --filter name=smartnursing-crei) ] 
then
    docker start -ai smartnursing-crei-1
else
    docker attach smartnursing-crei-1
fi
exit 0
