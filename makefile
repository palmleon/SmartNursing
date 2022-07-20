SHELL := /bin/bash
PROJECT_NAME := smartnursing
green := $(shell echo -e '\033[0;32m')
yellow := $(shell echo -e '\033[1;33m')
nc := $(shell echo -e '\033[0m')

all: stop clean build run

.PHONY:
build:
	@if [ -z "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo -e "$(yellow)Building the images...$(nc)"; \
	docker compose build ; \
	fi
	@echo "$(green)OK: Images built!$(nc)"
	

.PHONY:
clean: stop
	@if [ -n "$$(docker images --format {{.Repository}} | grep $(PROJECT_NAME))" ] ; \
	then echo -e "$(yellow)Removing the containers...$(nc)"; \
	docker compose down --rmi all; \
	fi
	@echo -e "$(green)OK: Everything cleaned!$(nc)" 

.PHONY:
run: stop #Only one container at a time
	@echo -e "$(yellow)Launching the containers...$(nc)"
	@docker compose up -d
	@echo -e "$(green)Containers launched!$(nc)"
#	@docker run  --name crei -it --link cdrsi:localhost --net SmartNursing_default rei

.PHONY:
stop:
	@if [ -n "$$(docker ps  --format {{.Names}} | grep $(PROJECT_NAME))" ] ; \
	then echo -e "$(yellow)Stopping the containers...$(nc)"; \
	docker compose down; \
	echo -e "$(green)Containers stopped!$(nc)"; \
	fi

