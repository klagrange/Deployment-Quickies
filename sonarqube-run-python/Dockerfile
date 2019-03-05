FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install curl -y
RUN apt-get install zip unzip -y
RUN apt-get install python3-pip -y

# install pylint3
RUN echo "Asia/Singapore" > /etc/timezone
RUN DEBIAN_FRONTEND=noninteractive apt-get install tzdata -y -f
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install pylint -y

# install sonar-scanner
WORKDIR /usr/src/sonarqube

RUN curl -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.3.0.1492-linux.zip -o sonar-scanner-3.3.0.1492-linux.zip

RUN unzip sonar-scanner-3.3.0.1492-linux.zip

# run unit test reports and send them over to sonarqube via the scanner
# run linting reports as well, and them over to sonarqube via scanner
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install coverage

RUN pip3 install pytest-cov

COPY . .

RUN coverage erase

RUN py.test --cov --cov-report xml

# RUN pylint *.py --reports=y --exit-zero > pylint-report.txt

RUN pylint -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero *.py > pylint-report.txt 

CMD ["/usr/src/sonarqube/sonar-scanner-3.3.0.1492-linux/bin/sonar-scanner"]
