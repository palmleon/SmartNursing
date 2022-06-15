SHELL := /bin/bash
PROJECT_NAME := smartclinic

all: stop clean build run

.PHONY:
build:
	@if [ -z "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Creating the images..."; \
	docker compose build ; \
	fi
	

.PHONY:
clean: stop
	@if [ -n "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Removing the containers..."; \
	docker compose down --rmi all; \
	fi

.PHONY:
run: stop #Only one container at a time
	@echo "Launching the containers..."
	@docker compose up -d
	@#docker run  --name crei -it --link cdrsi:localhost --net smartclinic_default rei

stop:
	@if [ -n "$$(docker ps  --format {{.Names}} | grep $(PROJECT_NAME))" ] ; \
	then echo "Stopping the containers"; \
	docker compose down; \
	fi
	@#echo "Stopping the containers (if present)..."
	@#docker compose down

