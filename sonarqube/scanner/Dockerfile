FROM openjdk:8

LABEL maintainer="Keith Lagrange <keith@bambu.life>"

RUN apt-get update
RUN apt-get install -y curl git tmux htop maven sudo

# Install Node - allows for scanning of Typescript
RUN curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
RUN sudo apt-get install -y nodejs build-essential

# Set timezone
ENV TZ=Asia/Singapore
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /root

RUN curl --insecure -o ./sonarscanner.zip -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.3.0.1492-linux.zip

RUN unzip sonarscanner.zip && \
    rm sonarscanner.zip && \
	mv sonar-scanner-3.3.0.1492-linux sonar-scanner

ENV SONAR_RUNNER_HOME=/root/sonar-scanner
ENV PATH $PATH:/root/sonar-scanner/bin

COPY ./sonar-runner.properties ./sonar-scanner/conf/sonar-scanner.properties

# Use bash if you want to run the environment from inside the shell, otherwise use the command that actually runs the underlying stuff
# CMD /bin/bash

# RUN cd ./src

# CMD /bin/bash

CMD sonar-scanner -X
