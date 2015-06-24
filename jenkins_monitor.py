#!/usr/bin/python

import requests, json, sys, time, serial
from struct import *

led_count = 12

if len(sys.argv) < 3:
	print 'Missing Job name and username'
	exit(1)

def is_current_user_build(username, job_json):
	actions = job_json['actions']
	parameters = None
	for action in actions:
		if 'parameters' in action:
			parameters = action['parameters']

	if parameters == None:
		return False

	for parameter in parameters:
		if parameter['name'] == 'CURRENT_BRANCH' and username in parameter['value']:
			return True

	return False

def get_led_constant_cmd(led, r, g, b):
	return pack('!BBBBB', led, 2, r, g, b)
	
def get_led_fade_cmd(led, r, g , b):
	return pack('!BBBBB', led, 0, r, g, b)

def get_led_blink_cmd(led, r, g , b):
	return pack('!BBBBB', led, 1, r, g, b)

def reset_leds(serial):
	# Reset all leds
	command = ""
	for i in range(0,led_count):
		command += get_led_constant_cmd(i, 0, 0, 0)

	serial.write(command)
	serial.flush()

def open_serial(device, baudrate):
	ser = serial.Serial(device, baudrate)

	# The arduino take some times to boot after reset, let it cool
	time.sleep(1)
	ser.flush()
	return ser

url_base = 'https://hudson.kalray.eu:8443/jenkins/'
job_url = url_base + 'job/' + sys.argv[1] + '/lastBuild/api/json'
username = sys.argv[2]
print 'Checking for user jobs for ' + username

serial = open_serial('/dev/ttyUSB0', 9600)

build_number = 0
job_failed = False;
print 'Polling job_url ' + job_url
while True:
	r = requests.get(job_url, verify=False)
	job_status = r.json()

	if build_number != job_status['number']:
		reset_leds(serial)
		build_number = job_status['number']
		job_failed = False
		print 'Job number : ' + str(build_number)

	command = ''
	user_build = is_current_user_build(username, job_status)
	
	if job_failed and user_build:
		serial.write(get_led_fade_cmd(5, 255, 0, 0))
	elif user_build:
		command += get_led_constant_cmd(5, 0, 255, 0)

	i = 0
	for build in job_status['subBuilds']:
		if build['result'] == 'SUCCESS':
			command += get_led_constant_cmd(i, 0, 0, 255)
		if build['result'] == None:
			command += get_led_fade_cmd(i, 0, 0, 255, 0)
		if build['result'] == 'FAILURE':
			command += get_led_constant_cmd(i, 255, 0, 0)
			job_failed = True
		i += 1

	if len(command) > 0:
		serial.write(command)


	time.sleep(2)
