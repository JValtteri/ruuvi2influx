# Ruuvi2influx
**Log RuuviTag data to [InfluxDB](https://www.influxdata.com/) from multiple [RuuviTags](https://ruuvi.com/).**

[![Docker Image Build](https://github.com/JValtteri/ruuvi2influx/actions/workflows/build-docker-image.yml/badge.svg)](https://github.com/JValtteri/ruuvi2influx/actions/workflows/build-docker-image.yml)

**For Docker implementation see [**Docker Version**](#docker-version)**

Influx database needs to be set up separately. I recommend the official [influxdb](https://hub.docker.com/_/influxdb) docker image for platforms that support it. Instructions for a full deployment can be found under [Example Setup](#example-setup) or more detailed, but old and cluttered instructions in[ruuvitags-raspberrypi-zero](https://github.com/JValtteri/ruuvitags-raspberrypi-zero) repository.

## Table of contents

- [Compatability](#compatability)
  - [Hardware](#hardware-requirements)
  - [Software Requirements](#software-requirements-for-local-instals)
- [Features](#features)
- [**Docker Version**](#docker-version)
  - [Configure](#configure)
  - [Run the ready image](#run-the-ready-image)
  - [or Build the image yourself](#or-build-the-image-yourself)
- [**Install locally**](#install-locally)
  - [Automatically](#automatically)
  - [Manually](#manually)
- [Config](#config)
  - [Sample Interval](#sample-interval)
  - [Event Queue](#event-queue)
  - [InfluxDB](#influxdb)
  - [Ruuvitags](#ruuvitags)
- [Run](#run)
- [Appendix](#appendix)
  - [Setup InfluxDB](#setup-influxdb)
  - [Setup Grafana](#setup-grafana)

---------

## Compatability

| **OS:** | Linux |
| :-- | :-- |
| **Architecture:** | ARMv7, ARM64 |

**Docker images may not be available for all platforms, but can be built with the included script.*

Docker support for `arm/v6` i.e. **Pi Zero W** support had to be dropped unfortunately, because compatible base images have been discontinued.
[Local install](#install-locally) option is still available and works on `arm/v6`.

### Hardware Requirements ###

- Bluetooth: Such as the one integrated into Raspberry **Pi Zero W** and later
- RuuviTags: RuuviTag RAW-format is used.

### Software Requirements for Local Instals:
- [Python 3.6+](https://docs.python.org/) or newer
- Linux OS
- Bluez (requires Linux)
- [RuuviTag Sensor Python Package](https://github.com/ttu/ruuvitag-sensor) (v1.2.1) by [Tomi Tuhkanen](https://github.com/ttu)
- [influxdb-python](https://github.com/influxdata/influxdb-python) library

## Features ##
- Listens  to selected RuuviTags
- Collects:
  - Temperature
  - Humidity
  - Pressure
  - Voltage
- Outputs measurements to `stdout`
- Send to InfluxDB via HTTP
- Optional data processing and filtering
- Configurable with config.yml
- [Docker ready](#docker-version)

---------

## Docker Version

Docker images are now built automatically usign GitHub actions.

Stable images are published on release:
```
ghcr.io/jvaltteri/ruuvi2influx:latest
ghcr.io/jvaltteri/ruuvi2influx:{version number}
```

Tip of `master` branch is published as `dev`:
```
ghcr.io/jvaltteri/ruuvi2influx:dev
```

Old docker hub page for `arm/v6` image: *https://hub.docker.com/r/jvaltteri/ruuvi2influx*. Using the outdated image is not recommended. It's better to [install on bare metal](#install-locally).

Instructions for setting up everything else: [ruuvitags-raspberrypi-zero](https://github.com/JValtteri/ruuvitags-raspberrypi-zero)

### Table of contents

- [Pull The Docker Image](#pull-the-docker-image)
- [Configure](#configure)
- [Run the ready image](#run-the-ready-image)
- [or Build the image yourself](#or-build-the-image-yourself)

### Configure

Create a `config.yml` in the same directroy, where you'll be starting the container from.

You can use the [**example_config.yml**](example_config.yml) as a template.
See [**Config**](#config) section for detais.

### Run the ready image using Docker Compose

```
docker compose up
```

### or Build the image yourself

To build a container compatible with your device run
```bash
$ docker build -f Debian.dockerfile --tag ruuvi2influx .
```

---------

## Install locally

### Automatically

```
$ sudo ./install.sh
```

### Manually

See the [instell script](./install.sh)

1. Install Python 3
2. Install and Update pip
3. Install bluez for bluetooth communication: `bluez` & `bluez-hcidump`
4. Install Python libraries (`requirements.txt`)

-----

## Config ##

Edit `config.yml` file and set desired settings.

| Key    | Default  | Explanation            |
| ----------------- | - | ------------------ |
| `"sample_interval"`  | 2 | Time between pings |
| `"event_queue"`     | 15000 | How meny pings are buffered if network is interrupted. |
| `"db_name"`         | "db" | The InfluxDB name |
| `"db_user"`         | "user" | Username to log in to the InfluxDB |
| `"db_password"`     |   | the InfluxDB password |
| `"db_host"`         | "localhost" | the address to the InfluxDB. ```!! omit 'https:\\' !!``` |
| `"db_port"`         | 8086 | Port used to connect to the InfluxDB |

### Sample Interval

Note: the sample interval effects only the *minimum* time between
outputting new datapoints. Listening is constant. If you are building a
databace, you may use this to limit the data resolution to a reasonable
rate.

The measurements from the sample interval are collected and averaged.
The result is sent forward to the databace. This reduces databace
bloat and makes queries faster.

To turn off filtering and internal processing, set sample_interval to 0.
Do this if you have room for a large databace and processing power for
large queries and want to controll all the processing yourself.

For light weight Raspberry Pi setup, the 60-900 seconds should be fine.

```yaml
# SAMPLE INTERVAL

sample_interval: 60 # seconds
```


### Event Queue

If the connection to the databace is interrupted, this many measurements
should be held in queue, untill connection resumes.

Large queue takes up RAM. When connection resumes, a very large WRITE reaquest
may be rejected by the DB.

```yaml
# EVENT QUEUE

event_queue: 15000
```

### InfluxDB

Settings for the HTTP connection to your InfluxDB

```yaml
# INFLUX DB
db: True                                        # Enable or disable database
db_name: ruuvitags
db_user: sensor
db_password: password
db_host: 127.0.0.1
db_port: 8086
```


### Ruuvitags

List the MAC addresses for your tags and give them names:

```yaml
# RUUVITAGS
# List and name your tags
tags:
  "CC:CA:7E:52:CC:34": Backyard
  "FB:E1:B7:04:95:EE": Upstairs
  "E8:E0:C6:0B:B8:C5": Downstairs
```

-----

## Run ##

You can run manually:

```bash
$ ./ruuvi2influx.py
OR
$ python3 ruuvi2influx.py
```

For non-docker setups it is recommended to setup a start script utilizing `screen`

```bash
screen -S logger -d -m python3 ruuvi2influx.py
```

There's a script provided for that purpose:
```
start_logger.sh
```

-------

## Appendix

The **influxdb** needs to be [installed](#setup-influxdb) seperately. If you don't already have a system for [visualizing](https://play.grafana.org/d/000000012/grafana-play-home?orgId=1) the data. I recommend [Grafana](https://grafana.com/).

For [***legacy***](https://github.com/JValtteri/ruuvi2influx/tree/legacy) version with MySQL and Dweet support, see the [***legacy***](https://github.com/JValtteri/ruuvi2influx/tree/legacy) branch

### PiZero compatible images

There are no longer any Raspberry Pi Zero W (ARMv6) compatible images for `influxdb`, nor `grafana`. It's recommended to use a **Pi 3** or newer for hosting **Influxdb-v1** and **Grafana**. Official ```grafana/grafana:latest``` image supports **ARMv7** and newer.

### Example setup

#### `docker-compose.yml`

Here is a docker compose for running Influxdb v1.8

```docker compose
services:
  influxdb:
    image: influxdb:1.8
    container_name: influxdb
    ports:
      - "8086:8086"
    volumes:
      - /home/pi/influxdb/influxdbdata/:/var/lib/influxdb/data/
      - /home/pi/influxdb/influxdbmeta/:/var/lib/influxdb/meta/
      - /home/pi/influxdb/influxdb.conf:/var/lib/influxdb/influxdb.conf:ro
    # --- Security Hardening --- #
    cap_drop:           # Drop all kernel capabilities for security
      - SYS_MODULE
      - ALL
    cap_add:
      - DAC_OVERRIDE
    # ---                    --- #

    ## User/Group == influxdb:influxdb
    ## UID/GID = 1500:1500

    restart: unless-stopped

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - 3000:3000
    volumes:
      - grafana-storage:/var/lib/grafana
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_NAME=Koti

    restart: unless-stopped
```

#### Setting everything up

- You need to configure the database (`influxdb.conf`)
    - `sudo docker run --rm influxdb:[version] influxd config > influxdb.conf.default`
    - `[data]` / `cache-max-memory-size` = `"512m"`
        - Limits the amount of memory influxdb will allocate to itself
    - `[data]` / `max-concurrent-compactions` = `2`
        - Use max two cores to perform compactions
    - `[monitor]` / `store-enabled` = `false`
        - Disables internal monitoring. This causes a lot of performance
          issues on Raspberry when enabled:
          <https://github.com/influxdata/influxdb/issues/9475>

- Create user `influxdb:influxdb` and set permissions
    - `chown -R influxdb:influxdb influxdbdata`
    - `chown -R influxdb:influxdb influxdbmeta`
- You need to setup the database (enter bunch of commands)
    - `docker exec -it influxdb /bin/ash`
    - `CREATE USER admin WITH PASSWORD '[admin_password]' WITH ALL PRIVILEGES`
    - `CREATE DATABASE "ruuvitags"`
    - `CREATE USER "sensor" WITH PASSWORD '[write_password]'`
    - `CREATE USER "grafana" WITH PASSWORD '[read_password]'`
    - `GRANT WRITE ON ruuvitags TO sensor`
    - `GRANT READ ON ruuvitags TO grafana`
- In Grafana, go to **Connections > Data sources**
    - Query language: `InfluxQL`
    - URL: `http://[influxdb IP]:8086`
    - Basic auth: `enable`
        - User: `grafana`
        - Password: `[read_password]`
    - Database: `ruuvitags`
    - User: `grafana`
    - Password: `[read_password]`
    - HTTP Method: `POST`
- Create a custom Dashboard in Grafana
