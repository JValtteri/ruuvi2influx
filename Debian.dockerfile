# syntax=docker/dockerfile:1
FROM debian:bullseye-slim
ENV TZ=Europe/Helsinki

WORKDIR /app

# Update
RUN apt-get update
RUN apt-get -y upgrade

# Install Python3
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip

# Install requirements
COPY requirements_minimal.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get -y install bluez
RUN apt-get -y install bluez-hcidump
RUN apt-get -y install bluez-deprecated

# Cleanup
RUN apt-get clean

# Copy Py files
COPY *.py ./
COPY LICENSE .
COPY README.md .
COPY entrypoint.sh .

ENTRYPOINT [ "entrypoint.sh"]
