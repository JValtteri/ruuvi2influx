# syntax=docker/dockerfile:1
FROM python:3.10.5-alpine3.16
ENV TZ=Europe/Helsinki

WORKDIR /usr/src/app

# Update
RUN apk update
RUN apk upgrade

# Python3
# Python3 already installed
RUN pip install --upgrade pip
# RUN /usr/local/bin/python -m pip install --upgrade pip

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add bluez-hcidump
RUN apk add bluez-deprecated

# Cleanup
RUN apk clean

COPY *.py ./
COPY LICENSE .
COPY README.md .
COPY alpine_entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

CMD ./entrypoint.sh
