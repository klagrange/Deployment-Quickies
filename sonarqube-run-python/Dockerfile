FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install curl -y
RUN apt-get install zip unzip -y
RUN apt-get install python3-pip -y

WORKDIR /usr/src/sonarqube

RUN curl -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.3.0.1492-linux.zip -o sonar-scanner-3.3.0.1492-linux.zip

RUN unzip sonar-scanner-3.3.0.1492-linux.zip

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install coverage

RUN pip3 install pytest-cov

COPY . .

RUN coverage erase

RUN py.test --cov --cov-report xml

CMD ["/usr/src/sonarqube/sonar-scanner-3.3.0.1492-linux/bin/sonar-scanner"]
