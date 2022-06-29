# RuuviTag-logger
Log RuuviTags data to SQLite database and Dweet.io and show charts on the RPi's website

# Work in progress

----------

## Used elements
  - ~~[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)~~
  - [Python 3](https://docs.python.org/3.6/)
  - [RuuviTag Sensor Python Package](https://github.com/ttu/ruuvitag-sensor) by [Tomi Tuhkanen](https://github.com/ttu)
  - ~~[Flask microframework](http://flask.pocoo.org/)~~
  - ~~[SQLite 3 database](https://docs.python.org/3.6/library/sqlite3.html#module-sqlite3)~~
  - [Data processing and interrupts](https://github.com/JValtteri/wstation) by [J.V.Ojala](https://github.com/JValtteri)

## Install



## Setup logger

Edit `config.yml` file and set desired settings.

List and name your tags:

```python
tags = [
    ['CC:CA:7E:52:CC:34', '1: Backyard'],
    ['FB:E1:B7:04:95:EE', '2: Upstairs'],
    ['E8:E0:C6:0B:B8:C5', '3: Downstairs']
]
```

Choose a sample rate you wish:

```python
sample_rate = 60 # seconds
```

note, the sample rate effects only the *minimum* time between outputting new datapoints. Listening is constant. If you are building a databace, you may use this to limit the data to a reasonable rate.

RuuviTag default RAW-format is used.

If you want to save data to local database, enable it:

```python
db = True # Enable or disable database saving True/False
```

Set execution rights to the file:

```bash
$ chmod +x ruuvitag-logger.py
```

Now you can try to run it manually:

```bash
$ ./ruuvitag-logger.py
OR
$ python3 ruuvitag-logger.py
```

It is recommended to setup a start script utilizing `screen`

```bash
screen -S logger -d -m python3 ruuvitag-logger.py
```

## Setup web-server



## Run as a docker container

Debian (working)
```bash
$ docker run --net=host --cap-add=NET_ADMIN --mount type=bind,source="$(pwd)"/config.yml,target=/app/config.yml,readonly ruuvitag-logger-py:debian
```

Alpine (in-progress, not working)
```bash
$ docker run --net=host --cap-add=NET_ADMIN --mount type=bind,source="$(pwd)"/config.yml,target=/usr/src/app/config.yml,readonly ruuvitag-logger-py:alpine
```

### Docker images

...
