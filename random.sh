#!/bin/bash

if [ -n "$(docker ps  --format "{{.Names}}" | grep smartclinic-*)" ] ;\ then echo "Stopping the containers"; docker compose down; fi;