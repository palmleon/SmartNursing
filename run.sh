docker compose up -d
docker run  --name crei -it --link cdrsi:localhost --net smartclinic_default rei