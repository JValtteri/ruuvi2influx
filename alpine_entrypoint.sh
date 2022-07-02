#!/bin/ash

# start services
service dbus start
service bluetooth start

# wait for startup of services
msg="Waiting for services to start..."
sleep=5

# reset bluetooth adapter by restarting it
# sudo hciconfig hci0 down
# sudo hciconfig hci0 up

python3 ruuvi2influx.py
