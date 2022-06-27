#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# J.V.Ojala 7.5.2020
# wcollector

# Copyright for portions of project RuuviTag-logger are held by
# Dima Tsvetkov author, 2017 as part of project RuuviTag-logger and
# are licensed under the MIT license.
# Copyright for other portions of project RuuviTag-logger are held by
# J.V.Ojala, 2020 as part of project wcollector. For license, see
# LICENSE


from ruuvitag_sensor.ruuvi import RuuviTagSensor
from datetime import datetime
import time
import yaml
import queue
from sender import Sender
# from logging import log
from logger import Logger
logger = Logger(__name__)

class Configuration():

	def __init__(self):
		config = self.readConfig()

		self.column_width = config['column_width']		# 14 normal
		self.sample_interval = config['sample_interval'] # seconds

		# list all your tags [MAC, TAG_NAME]
		self.tags = config['tags']
		self.queue_depth = config["event_queue"]

		self.db = config['db'] # Enable or disable database saving True/False

		# self.db_name = config["db_name"]
		# self.db_user = config["db_user"]
		# self.db_password = config["db_password"]
		# self.host = config["db_host"]
		# self.port = config["db_port"]


	def readConfig(self):
		"""
		Reads the config file and returns the dict of
		all settings.
		"""

		filename = "config.yml"

		try:
			configfile = open(filename, 'r')
		except FileNotFoundError:
			print("Error: Could not find %s" % filename)
			exit()

		settings = yaml.load(configfile, Loader=yaml.SafeLoader)
		configfile.close()

		return settings


class Handler():

	def __init__(self, config):

		self.event_queue = queue.Queue(config.queue_depth)
		self.body = [
		{
		    "tags": {
		        "target": "",
		        "name": "Test",
		        "id": "0",
		        "location": "Test"
		    },
		    "time": 0,
		    "fields": {
		        "value": 1
		    }
		}
		]

		self.db_name = config.db_name
		self.db_user = config.db_user
		self.db_password = config.db_password
		self.host = config.host
		self.port = config.port

		self.sender_thread = Sender(self.event_queue, self.body, self.db_name, self.db_user, self.db_password, self.host, self.port)
		self.sender_thread.daemon=True

	def handle_data(self, found_data):
		# This is the callback that is called every time new data is found

		# add or update fresh data with the found tag
		if found_data[0] in State.tags:
			State.tags[found_data[0]].add(found_data)

		# Get the time
		now = datetime.timestamp(datetime.now())
		time_passed = now - State.last_update_time

		# If the sample window has closed
		if time_passed >= config.sample_interval:

			State.last_update_time = now

			dbData = {}

			for i in State.tags:
				tag = State.tags[i]

				# Updates the processed values in the Tag object
				print("")
				print(datetime.now())
				tag.update()
				dbData[tag.mac] = {'name': tag.name}

				# Print values to terminal
				print(title())
				print(data_line('temp', 'C'))
				print(data_line('pres', 'hPa'))
				print(data_line('humi', '%'))
				print(data_line('batt', 'V'))

				# Prepare DB Data
				dbData[tag.mac].update({"temperature": tag.temp})
				dbData[tag.mac].update({"pressure": tag.pres})
				dbData[tag.mac].update({"humidity": tag.humi})
				dbData[tag.mac].update({"voltage": tag.batt})

			if config.db:
				# save data to db
				posix = round( time.time() * 1000 )
				for mac, content in dbData.items():

					item = content
					item["mac"] = mac
					item["time"] = posix

					# Put item to queue
					try:
						self.event_queue.put(item)
					except queue.Full:
						logger.error("queue.FULL")

					# If no thread is active, restart the thread
					if not self.sender_thread.is_alive():
						self.sender_thread = Sender(self.event_queue, self.body, self.db_name, self.db_user, self.db_password, self.host, self.port)
						self.sender_thread.daemon=True
						self.sender_thread.start()


class State():
	"Holds the state of things"
	last_update_time = datetime.timestamp(datetime.now())
	# All tags are collected here
	tags = {}


class Tag():
	'''
	Holds all data related to a tag
	'''
	def __init__(self, mac, name):

		self.mac = mac
		self.id = mac[-6:]	# A short ID
		self.name = name
		# The raw values
		self._temp = []
		self._humi = []
		self._pres = []
		self._batt = []
		# The probeable values
		self.temp = 0
		self.humi = 0
		self.pres = 0
		self.batt = 0

	def add(self, found_data):
		'''
		Add a new set of values to the Tag object.
		'''
		self._temp.append( found_data[1]['temperature'] )
		self._humi.append( found_data[1]['humidity'] )
		self._pres.append( found_data[1]['pressure'] )
		self._batt.append( found_data[1]['battery']/1000 )

	def update(self):
		'''
		Updates the object stored values with the calculated average of
		values received since last update.
		Re-initializes the object to collect a new series of data.
		If no new datapoints were received, the previous data point is
		retained.
		'''
		try:
			self.temp = round( avg( self._temp ), 2)
		except ZeroDivisionError:
			pass	# If no new datapoints exist, don't change the stored value

		try:
			self.humi = round( avg( self._humi ), 2)
		except ZeroDivisionError:
			pass

		try:
			self.pres = round( avg( self._pres ), 2)
		except ZeroDivisionError:
			pass

		try:
			self.batt = round( avg( self._batt ), 3)
		except ZeroDivisionError:
			pass

		self._temp = []
		self._humi = []
		self._pres = []
		self._batt = []


def data_line(subject, unit=""):
	'''
	Returns data from all sensors of the selected type (subject)
	formated in a row.
	Use: print( data_line('pres','hPa') )
	'''
	datas = []
	dline = ""
	for i in State.tags:
		tag = State.tags[i]
		# try:
		if subject == 'temp':
			avg_data = tag.temp

		elif subject == 'pres':
			avg_data = tag.pres

		elif subject == 'humi':
			avg_data = tag.humi

		elif subject == 'batt':
			avg_data = tag.batt

		else:
			print(tag, 'foo', subject)

		# 1.321 + " " + "V"
		value = str(avg_data) + " " + unit
		datas.append( value.ljust(config.column_width) )


	dline = ''.join(datas)
	return dline


def title():
	'''
	Returns the header associated with data_line()
	Use: print( title() )
	'''

	titles = []
	for i in State.tags:
		titles.append( (State.tags[i].id).ljust(config.column_width) )

	dtitle = ''.join(titles)
	return dtitle


def avg(lst):
	'''
	returns the average of the list
	'''
	return sum(lst) / len(lst)


if __name__ == "__main__":

	config = Configuration()
	handler = Handler(config)

	print("\nListened macs")

	# Collects initialized tags
	macs = config.tags
	for mac in macs:
		State.tags[mac] = Tag(mac, macs[mac])
		print(State.tags[mac].mac)

	# The recommended way of listening to current Ruuvitags, using interrupts
	RuuviTagSensor.get_datas(handler.handle_data)
