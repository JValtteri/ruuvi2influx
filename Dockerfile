# syntax=docker/dockerfile:1
# Custom RPiZero compatible image
#FROM python:3-alpine
FROM python:3.10.5-alpine3.16
ENV TZ=Europe/Helsinki

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
COPY install.sh install.sh

RUN chmod +x install.sh
RUN install.sh

COPY *.py .
COPY LICENSE .
COPY README.md .

ENTRYPOINT [ "sudo", "python3", " ruuvitag-logger.py" ]
