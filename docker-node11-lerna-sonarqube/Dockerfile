FROM node:11
RUN npm install -g yarn lerna
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install default-jdk python-pip -y
RUN pip install requests
