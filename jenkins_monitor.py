#!/usr/bin/python

import requests, json, sys, time, serial
from struct import *

if len(sys.argv) < 3:
	print "Missing Job name and username"
	exit(1)

def is_current_user_build(username, job_json):
	actions = job_json['actions']
	parameters = actions[0]['parameters']

	for parameter in parameters:
		if parameter['name'] == 'CURRENT_BRANCH' and username in parameter['value']:
			return True
			
	return False

def reset_leds(serial):
	# Reset all leds
	command = ""
	for i in range(0,6):
		command += pack('!BBBBB', i, 2, 0, 0, 0)

	serial.write(command)
	serial.flush()

def open_serial(device, baudrate):
	ser = serial.Serial(device, baudrate)

	# The arduino take some times to boot after reset, let it cool
	time.sleep(1)
	ser.flush()
	return ser

url_base = "https://localhost:8443/jenkins/"
job_url = url_base + "job/" + sys.argv[1] + "/lastBuild/api/json"
username = sys.argv[2]
print "Checking for user jobs for " + username

serial = open_serial('/dev/ttyUSB1', 9600)

build_number = 0
print "Polling job_url " + job_url
while True:
	r = requests.get(job_url, verify=False)
	job_status = r.json()
	
	if build_number != job_status['number']:
		reset_leds(serial)
		build_number = job_status['number']
		print "Job number : " + str(build_number)
	
	command = ""
	if is_current_user_build(username, job_status):
		command += pack('!BBBBB', 5, 2, 0, 255, 0)

	i = 0
	for build in job_status['subBuilds']:
		if build['result'] == 'SUCCESS':
			command += pack('!BBBBB', i, 2, 0, 0, 255)
		if build['result'] == None:
			command += pack('!BBBBBH', i, 0, 0, 0, 255, 0)
		if build['result'] == 'FAILURE':
			command += pack('!BBBBB', i, 2, 255, 0, 0)
		i += 1

	if len(command) > 0:
		serial.write(command)

	time.sleep(2)
