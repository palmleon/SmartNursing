#!/bin/bash
cd Fibrillation;
docker build -t fi .
cd ..
cd device-registry-system 
docker build -t drsi .
cd ..
cd PatientMonitor
docker build -t pmi .
cd ..
cd light-patient-room-monitor
docker build -t lprmi  .
cd ..
cd temperature-common-room
docker build -t tcri .
cd ..
cd temperature-patient-room
docker build -t tpri .
cd ..
cd thingSpeakAdaptor
docker build -t  tsai .
cd ..
cd raspberry-emulator
docker build -t  rei .
cd ..

cd Telegram
docker build -t  ti .
cd ..

cd PatientDeviceAnalyzer
docker build -t  dai .
cd ..

cd DataAnalysis
docker build -t dai .
cd ..

docker compose up -d
docker run  --name crei -it --link cdrsi:localhost --net smartclinic_default rei
