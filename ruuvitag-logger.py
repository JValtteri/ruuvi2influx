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

class Configuration():

	def __init__(self):
		config = self.readConfig()

		self.column_width = config['column_width']		# 14 normal
		self.sample_rate = config['sample_rate'] # seconds

		# list all your tags [MAC, TAG_NAME]
		self.tag_macs = config['tag_macs']

		self.dweet = config['dweet'] # Enable or disable dweeting True/False
		self.dweetUrl = config['dweetUrl'] # dweet.io url
		self.dweetThing = config['dweetThing'] # dweet.io thing name

		self.db = config['db'] # Enable or disable database saving True/False
		self.dbFile = config['dbFile'] # path to db file


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

		settings = yaml.load(configfile)
		configfile.close()

		return settings

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

config = Configuration()


if config.dweet:
	import requests
'''
Dweet format:
{
	'TAG_NAME1 temperature': VALUE,
	'TAG_NAME1 humidity': VALUE,
	'TAG_NAME1 pressure': VALUE,
	'TAG_NAME2 temperature': VALUE,
	'TAG_NAME2 humidity': VALUE,
	'TAG_NAME2 pressure': VALUE,
	etc...
}
'''
if config.db:
	import sqlite3

print("\nListened macs")

# Collects initialized tags
for i in config.tag_macs:
	State.tags[i[0]] = Tag(i[0], i[1])
	print(State.tags[i[0]].mac)	#DEBUG


def db_lock():
	# open database
	conn = sqlite3.connect(config.dbFile)

	# check if table exists
	cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensors'")
	row = cursor.fetchone()
	if row is None:
		print("DB table not found. Creating 'sensors' table ...")
		conn.execute('''CREATE TABLE sensors
			(
				id			INTEGER		PRIMARY KEY AUTOINCREMENT	NOT NULL,
				timestamp	NUMERIC		DEFAULT CURRENT_TIMESTAMP,
				mac			TEXT		NOT NULL,
				name		TEXT		NULL,
				temperature	NUMERIC		NULL,
				humidity	NUMERIC		NULL,
				pressure	NUMERIC		NULL,
				voltage		NUMERIC		NULL
			);''')
		print("Table created successfully\n")
	return conn


def dweet_out(dweetThing, dweetData):
	# send data to dweet.io
	print("Dweeting data for {} ...".format(dweetThing))
	response = requests.post(config.dweetUrl+dweetThing, json=dweetData)
	print(response)
	print(response.text)


def handle_data(found_data):
	# This is the callback that is called every time new data is found

	# add or update fresh data with the found tag
	if found_data[0] in State.tags:
		State.tags[found_data[0]].add(found_data)

	if config.db:
		conn = db_lock()

	# Get the time
	now = datetime.timestamp(datetime.now())
	time_passed = now - State.last_update_time

	# If the sample window has closed
	if time_passed >= config.sample_rate:

		State.last_update_time = now

		dweetData = {}
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

			# Prepare Dweet Data
			dweetData[tag.name+' '+"temperature"] = tag.temp
			dweetData[tag.name+' '+"pressure"] = tag.pres
			dweetData[tag.name+' '+"humidity"] = tag.humi
			dweetData[tag.name+' '+"voltage"] = tag.batt
			
			# Prepare DB Data
			dbData[tag.mac].update({"temperature": tag.temp})
			dbData[tag.mac].update({"pressure": tag.pres})
			dbData[tag.mac].update({"humidity": tag.humi})
			dbData[tag.mac].update({"voltage": tag.batt})

		if config.dweet:
			# Send a dweet
			dweet_out(config.dweetThing, dweetData)

		if config.db:
			# save data to db
			anow = time.strftime('%Y-%m-%d %H:%M:%S')
			for mac, content in dbData.items():
				conn.execute("INSERT INTO sensors (timestamp,mac,name,temperature,humidity,pressure,voltage) \
					VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {})".\
					format(anow, mac, content['name'], content['temperature'], content['humidity'], content['pressure'], content['voltage']))
			conn.commit()
			conn.close()


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


# The recommended way of listening to current Ruuvitags, using interrupts
RuuviTagSensor.get_datas(handle_data)
