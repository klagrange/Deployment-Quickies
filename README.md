# ERD
Quickly generate ER Diagrams based on *https://github.com/BurntSushi/erd*
```sh
$ # Create your er files and place them under the ./er folder
$ ./erd_ctl.sh
$ # Result: one pdf per er diagram defintion.
$ # Note: the rest of the files can be ignored.
```

# Quick docker install ubuntu
Script to install docker on system (ubuntu).

# Sonarqube
Quickly generate a dockerized sonarqube server with attached postgres db for persistence.
```sh
$ docker-compose up --build
```

# Sonarqube Run Python
100% dockerized sonar scanner for python 3.x.x project that sends coverage reports to a sonarqube server.
```sh
$ # files to adapt: sonar-project-properties
$ ./run-sonar-scanner.sh
```

# OCR Caffe dockerized
Containerized https://github.com/MichalBusta/DeepTextSpotter.git with all required depencies for OCR development.
```sh
docker build . -t XXX
./dev-remote-executer.sh /bin/bash
./dev-remote-executer.sh python
./dev-remote-executer.sh python api.py
```

# Naive deployment
Script to help deploy dockerized application on remote server based on ssh/scp connection.

# Docker node 11 sonarqube
base image node:11 with python (+request lib installed)
