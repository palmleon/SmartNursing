SHELL := /bin/bash
PROJECT_NAME := smartclinic

all: stop clean build run

.PHONY:
build:
	@if [ -z "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Building the images..."; \
	docker compose build ; \
	fi
	@echo "OK: Images built!"
	

.PHONY:
clean: stop
	@if [ -n "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Removing the containers..."; \
	docker compose down --rmi all; \
	fi
	@echo "OK: Everything cleaned!" 

.PHONY:
run: stop #Only one container at a time
	@echo "Launching the containers..."
	@docker compose up -d
	@#docker run  --name crei -it --link cdrsi:localhost --net smartclinic_default rei

stop:
	@if [ -n "$$(docker ps  --format {{.Names}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Stopping the containers"; \
	docker compose down; \
	else echo "No container running!"; \
	fi

