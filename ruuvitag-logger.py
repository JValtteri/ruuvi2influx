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

		self.db_name = config["db_name"]
		self.db_user = config["db_user"]
		self.db_password = config["db_password"]
		self.host = config["db_host"]
		self.port = config["db_port"]


		# Startup info
		logger.info("\nListened macs")

		# Collects initialized tags
		tags = self.tags
		for mac in tags:
			# Creates a Tag Object
			# with properties (mac, name)
			tag = Tag(mac=mac, name=tags[mac])
			# Saves a Teg Object in State Object
			State.tags[mac] = tag
			# Log the mac-address
			logger.info(State.tags[mac].mac)

		logger.info("db_name\t" + self.db_name)
		logger.info("db_user\t" + self.db_user)
		logger.info("db_host\t" + self.host)
		logger.info("db_port\t" + str(self.port) )


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
				"measurement": "ruuvitag",
				"tags": {
					"name": "Test",
					'mac': ""
				},
				"time": 0,
				"fields": {
				}
			}
		]

		self.db = config.db
		self.db_name = config.db_name
		self.db_user = config.db_user
		self.db_password = config.db_password
		self.host = config.host
		self.port = config.port

		self.sender_thread = Sender(self.event_queue, self.body, self.db_name, self.db_user, self.db_password, self.host, self.port)
		self.sender_thread.daemon=True


	def handle_data(self, found_data):
		# This is the callback that is called every time new data is found

		found_mac = found_data[0]

		# If state tags{} has an entry mac: Tag() for found_mac
		# Appends the found data values to their respevtive lists in the Tag object.
		if found_mac in State.tags:
			State.tags[found_mac].add(found_data)

		# Get the time
		now = datetime.timestamp(datetime.now())
		time_passed = now - State.last_update_time

		# If the sample window has closed, output the data
		# Stored in Tag() Objects
		if time_passed >= config.sample_interval:

			State.last_update_time = now
			self.outputs()


	def outputs(self):
		'''
		Outputs the data collected
		'''

		# Create a SET of data
		dbData = {}

		for tag_mac in State.tags:
			tag = State.tags[tag_mac]

			# Trigger caclulation of the output values:
			# -> Values collected since last update() are averaged
			#    and stored, buffers are reset.
			tag.update()

			# Create tag with a name
			dbData[tag.mac] = {'name': tag.name}

			# Prepare DB Data
			dbData[tag.mac].update({
				"temperature": tag.temp,
				"pressure": tag.pres,
				"humidity": tag.humi,
				"voltage": tag.batt
				})


		# Print values to terminal
		self.output_to_screen()

		if self.db:
			self.output_to_db(dbData)


	def output_to_db(self, dbData):
		"""
		Re-formats dbData as a flat dictionary
		Puts the result in send_queue
		"""

		# This function works, but is ugly.
		# It does redundant fiddling the data
		# to be fiddled with again.

		# Save data to db
		posix = round( time.time() * 1000 )
		for mac, item in dbData.items():

			item["mac"] = mac
			item["time"] = posix

			# If any one datapoint value ("temperature") is None
			# all datapoint values are None
			if item["temperature"] is not None:
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

			else:
				# Do not send datapoints with None values.
				# InfluxDB can't handle None values or empty {} values
				pass

		# Time for sender to finnish
		time.sleep(1)


	@staticmethod
	def output_to_screen():
		"""
		Outputs data to screen
		and/or selected LOG location
		"""
		logger.info("")
		logger.info(datetime.now())

		# Print values to terminal
		logger.info(title())
		logger.info(State.data_line('temp', 'C'))
		logger.info(State.data_line('pres', 'hPa'))
		logger.info(State.data_line('humi', '%'))
		logger.info(State.data_line('batt', 'V'))


class State():
	"Holds the state of things"
	last_update_time = datetime.timestamp(datetime.now())
	# All tags are collected here
	tags = {}

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
				logger.critical("Invalid tag subject: '{}', Units:, '{}'".format(subject, unit))
				raise Exception("Invalid tag subject: '{}'".format(subject))

			# 1.321 + " " + "V"
			value = str(avg_data) + " " + unit
			datas.append( value.ljust(config.column_width) )


		dline = ''.join(datas)
		return dline


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
		self.temp = None
		self.humi = None
		self.pres = None
		self.batt = None

	def add(self, found_data):
		'''
		Add a new set of values to the Tag object.
		'''
		self._temp.append( float( found_data[1]['temperature'] ) )
		self._humi.append( float( found_data[1]['humidity'] ) )
		self._pres.append( float( found_data[1]['pressure'] ) )
		self._batt.append( float( found_data[1]['battery']/1000 ) )

	def update(self):
		'''
		Updates the object stored values with the calculated average of
		values received since last update.
		Re-initializes the object to collect a new series of data.

		If no new datapoints were received, the data point set to None.
		'''
		try:
			self.temp = round( avg( self._temp ), 2)
		except ZeroDivisionError:
			self.temp = None	# If no new datapoints exist, set value to None

		try:
			self.humi = round( avg( self._humi ), 2)
		except ZeroDivisionError:
			self.humi = None

		try:
			self.pres = round( avg( self._pres ), 2)
		except ZeroDivisionError:
			self.pres = None

		try:
			self.batt = round( avg( self._batt ), 3)
		except ZeroDivisionError:
			self.batt = None

		self._temp = []
		self._humi = []
		self._pres = []
		self._batt = []


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

	# The recommended way of listening to current Ruuvitags, using interrupts
	try:
		RuuviTagSensor.get_datas(handler.handle_data)
	except KeyboardInterrupt:
		logger.info("KeyboardInterrupt: Exiting")
