#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# J.V.Ojala 12.11.2021
# network-probe

import time
import threading
import copy
from influxdb import InfluxDBClient, exceptions
from logger import Logger
logger = Logger(__name__)


class Sender(threading.Thread):
    '''A thread to send the ping analytics.'''

    def __init__(self, event_queue, body, db_name, db_user, db_password, db_host, db_port, daemon=True):

        threading.Thread.__init__(self)
        self.event_queue = event_queue
        self.body = body

        # Configuration
        self.host = db_host
        self.port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

        # Internal variables
        self.queue_warnined = False                 # Flag flips if queue grows alarmingly big
        self.queue_warning_threshold = 10800        # Queue size to trigger a warning


    def run(self):
        '''Thread main function'''
        logger.debug("Sender thread STARTED")
        messages=[]
        queue_size = self.event_queue.qsize()

        # Warns of large queue
        if queue_size > self.queue_warning_threshold:
                logger.warning("Large queue: {}".format(queue_size))
                self.queue_warnined = True

        while queue_size > 0:
            logger.debug("Queue size: {}".format(queue_size))

            item = self.event_queue.get()
            message = copy.deepcopy(self.message_map(item))
            if message is not None:
                # Adds message to a list to be sent
                messages.append(message[0])
                logger.debug("New message: {}".format(item))

                # Checks if queue has any new events
                queue_size = self.event_queue.qsize()

                # Warns if can't keep up
                if queue_size > self.queue_warning_threshold and self.queue_warnined == False:
                    self.queue_warnined = True
                    logger.warning("Can't keep up. Large queue: {}".format(queue_size))

        self.queue_warnined = False               # Warning is reset
        logger.debug("Sending")
        self.send( messages )
        logger.debug("Sent")
        logger.debug("Sender thread CLOSED")


    def message_map(self, item):
        '''Maps values in ITEM to message body'''
        # item = {key: value for (key, value) in _item if value is not None }
        message = copy.deepcopy(self.body)

        message[0]["tags"]["name"] = item["name"]
        message[0]["tags"]["mac"] = item["mac"]

        if item["temperature"] != None:
            message[0]["fields"]["temperature"] = item["temperature"]

        if item["pressure"] != None:
            message[0]["fields"]["pressure"] = item["pressure"]

        if item["humidity"] != None:
            message[0]["fields"]["humidity"] = item["humidity"]

        if item["voltage"] != None:
            message[0]["fields"]["voltage"] = item["voltage"]

        message[0]["time"] = round(item["time"])

        if message[0]["fields"] is not {}:
            return message
        if message[0]["fields"] is not {}:
            return None


    def send(self, message, retry_time=3):
        '''Sends the MESSAGE to influxDB'''
        logger.debug("Message: {}".format(message))
        client = InfluxDBClient(self.host, self.port, self.db_user, self.db_password, database=self.db_name, ssl=False, verify_ssl=False)
        sent = False
        while sent is False:
            try:
                client.write_points(message, time_precision='ms')
            except exceptions.InfluxDBClientError as error:
                logger.error("InfluxDB Error {}".format( str(error) ))
                logger.error("Retry in 3 s").format(retry_time)
                time.sleep(retry_time)
            except Exception as error:
                # Yep! This is ugly, but a failed connection raises a million different exceptions.
                # Any failure in sendin at this point is a connection error
                logger.error("Connection Error {}. Retry in {} s".format(str(error)), retry_time)
                time.sleep(retry_time)
            else:
                logger.debug("Send succesful!")
                sent = True

        client.close()
