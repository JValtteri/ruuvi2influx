# syntax=docker/dockerfile:1
FROM python:3.10.5-alpine3.16
ENV TZ=Europe/Helsinki

WORKDIR /usr/src/app

COPY requirements_minimal.txt requirements.txt
RUN apk update
RUN apk add bluez-deprecated
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY LICENSE .
COPY README.md .

# ENTRYPOINT [ "python3", "ruuvitag-logger.py" ]
