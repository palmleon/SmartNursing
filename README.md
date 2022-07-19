# SmartNursing

<p align="center">
<a href="https://imgbb.com/"><img src="https://i.ibb.co/Ny6wg11/polito-logo-new.png"></a>
</p>  
<p align="center">
 <img alt="Languages" src="https://img.shields.io/badge/language-Python-orange">
 <img alt="Version" src="https://img.shields.io/badge/python->=3.6-blue"/>
 <img alt="Version" src="https://img.shields.io/badge/version-1.0-blue"/>
  <img alt="Development" src="https://img.shields.io/badge/development-terminated-brightgreen"/>   
</p>

## Team

- <img alt="avatar" src="https://github.com/AmedeoSarpa.png" width="20px" height="20px"> **Amedeo Sarpa** - [AmedeoSarpa](https://github.com/AmedeoSarpa)
- <img alt="avatar" src="https://github.com/alessda.png" width="20px" height="20px"> **Alessandro D'Apice** - [alessda](https://github.com/alessda)
- <img alt="avatar" src="https://github.com/palmleon.png" width="20px" height="20px"> **Leonardo Palmucci** - [palmleon](https://github.com/palmleon)
- <img alt="avatar" src="https://github.com/LorenzoCentamore.png" width="20px" height="20px"> **Lorenzo Giuseppe Centamore** - [LorenzoCentamore](https://github.com/LorenzoCentamore)

## What is SmartNursing?

SmartNursing is a tool that assists nurses and physicians in a nursing home in taking care of the residents.

SmartNursing automates many tedious tasks like health status monitoring, data recording and analysis, emergency detection and communication, and environment management.

Besides, it comes with a UI based on Thingspeak to consult resident health data and a Telegram Bot used by nurses and physicians to manage the residents.

The system is supposed to be deployed on a Raspberry acting as the core system; additional gateway nodes, one per room, should gather information from the sensors and directly stream them to the core.

For didactic reasons, it was not possible to use neither the gateway nodes nor the sensors. So, the project comprises a  ```raspberry emulator``` to simulate sensors and their communication to the core.

## How to run SmartNursing

### Prerequisites

- Python (v. >= 3.6)
- Docker (v. >= 20)

### Run it!

**1**. Ensure that docker is running locally !

**2**. Open a terminal

**3**. Then, you can use the following commands:

- `make all` or `make`: launch SmartNursing
- `make stop`: stop SmartNursing (restart it by using `make run`)
- `make clean`: remove everything (images and containers)

**4**. If you want to use either the system terminal or the raspberry emulator, use the following scripts:

- `system_terminal.sh`
- `raspberry_emulator.sh`

## Services ID

The following services are supported:

- light-patient-monitor : 1
- patient monitor : 2
- fibrillation : 3
- temperature-common-room-monitor : 4
- temperature-patient-room-monitor : 5
- thingspeek : 6
- telegram : 7
- data-analysis : 8
- system terminal: 9
- patient-device-analyzer : 10
