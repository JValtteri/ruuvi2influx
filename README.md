# Ruuvi2influx
**Log RuuviTag data to [InfluxDB](https://www.influxdata.com/) from multiple [RuuviTags](https://ruuvi.com/).**
**From there, the [visualization](https://play.grafana.org/d/000000012/grafana-play-home?orgId=1) can be done with [Grafana](https://grafana.com/), for example.**

**For [***legacy***](https://github.com/JValtteri/ruuvi2influx/tree/legacy) version with MySQL and Dweet support, see the [***legacy***](https://github.com/JValtteri/ruuvi2influx/tree/legacy) branch**

## Compatability

ARMv6, ARMv7, ARM64, x86, AMD64 and others

### Requires:
- [Python 3.6+](https://docs.python.org/) or newer
- Linux OS
- Bluez (requires Linux)
- [RuuviTag Sensor Python Package](https://github.com/ttu/ruuvitag-sensor) by [Tomi Tuhkanen](https://github.com/ttu)
- [influxdb-python](https://github.com/influxdata/influxdb-python) library
- Hardware:
  - Bluetooth for example integrated in Raspberry **Pi Zero W** and later
  - RuuviTags: RuuviTag default RAW-format is used.

## Features ##
- Listenes to selected RuuviTags
- Collects:
  - Temperature
  - Humidity
  - Pressure
  - Voltage
- Outputs measurements to stdout
- Send to InfluxDB via HTTP
- Optional data processing and filtering
- Configurable with config.yml
- Docker ready

## Install


### Automatically

```
$ sudo ./install.sh
```

### Manually

#### Install Python 3 ###

```
$ sudo apt-get update
$ sudo apt-get install python3
$ sudo apt-get install python3-pip
```

#### Install and Update pip
```
sudo apt-get -y install python3-pip
sudo pip3 install --upgrade pip
```

#### Install bluez for bluetooth communication
```
sudo apt-get install bluez
sudo apt-get install bluez-hcidump
```
#### Install Python libraries
```
$ pip3 install -r requirements.txt
```

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
large queries and want to controll all the processing your self.

For light weight Raspberry Pi setup, the 60-900 seconds should be fine.

```yaml
# SAMPLE INTERVAL

sample_interval: 60 # seconds
```


### EVENT QUEUE

If the connection to the databace is interrupted, how meny measurements
should be held in queue, untill connection resumes.

Large queue takes up RAM. When connection resumes, a very large WRITE reaquest
may be rejected by the DB.

```yaml
# EVENT QUEUE

event_queue: 15000
```

### INFLUX DB

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


### RUUVITAGS

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

Now you can run it manually:

```bash
$ ./ruuvi2influx.py
OR
$ python3 ruuvi2influx.py
```

For non-docker setups it is recommended to setup a start script utilizing `screen`

```bash
screen -S logger -d -m python3 ruuvi2influx.py
```

Thre is a ready script for that
```
start_logger.sh
```

## Run as a docker container

### Build

To build a container compatible with your device run
```bash
$ docker build -f Debian.dockerfile --tag ruuvi2influx
```

### Run
Debian based image
```bash
$ docker run \
    -d \
    --name ruuvi \
    --restart unless-stopped \
    --net=host \
    --cap-add=NET_ADMIN \
    --mount type=bind,source="$(pwd)"/config.yml,target=/app/config.yml,readonly \
    ruuvi2influx:latest
```


### Light weight Alpine image
**Planned. Not working as of yet**
```bash
$ docker run
    -d \
    --name ruuvi \
    --restart unless-stopped \
    --net=host \
    --cap-add=NET_ADMIN \
    --mount type=bind,source="$(pwd)"/config.yml,target=/usr/src/app/config.yml,readonly \
    ruuvi2influx:alpine
```

-------

## Setup InfluxDB

**Official image**
```
docker pull influxdb:latest
```

**PiZero compatible image**
```
mendhak/arm32v6-influxdb
```

## Setup Grafana

**Official image**
```
docker pull grafana/grafana
```

**PiZero compatible image**

There doesn't seem to be any reasonably up-to-date version compatible with Raspberry Pi Zero W (ARMv6). It is recommended to use a **Pi 3** or newer for hosting **Grafana**. Official ```grafana/grafana:latest``` image supports **ARMv7** and newer.

I may yet try to build a Zero compatible image, but since I have a working image on another Pi, the incentive for me is low right now.
