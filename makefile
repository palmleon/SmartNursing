all: stop clean build run

.PHONY:
build:
	@echo "Creating the images..."
	@docker compose build 
	

.PHONY:
clean:
	@echo "Removing the containers..."
	@docker compose down --rmi all


.PHONY:
run: stop
	@echo "Creating and launching the containers..."
	@docker compose up -d
	@#docker run  --name crei -it --link cdrsi:localhost --net smartclinic_default rei

stop:
	@echo "Stopping the containers..."
	@docker compose down

