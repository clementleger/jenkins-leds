#!/usr/bin/python

import requests, json, sys, time, serial
from struct import *

url_base = "https://localhost:8443/jenkins/job/"

if len(sys.argv) < 2:
	print "Missing Job name"
	exit(1)

url = url_base + sys.argv[1] + "/lastBuild/api/json"

ser = serial.Serial('/dev/ttyUSB1', 9600)

time.sleep(3)
command = ""
for i in range(0,5):
	command += pack('!BBBBB', i, 2, 0, 0, 0)

ser.write(command)
ser.flush()

print "Polling url " + url
while True:
	r = requests.get(url, verify= False)
	job_status = r.json()
	
	i = 0
	command = ""
	for build in job_status['subBuilds']:
		if build['result'] == 'SUCCESS':
			command += pack('!BBBBB', i, 2, 0, 255, 0)
		if build['result'] == None:
			command += pack('!BBBBBH', i, 0, 0, 0, 255, 0)
		if build['result'] == 'FAILURE':
			command += pack('!BBBBB', i, 2, 255, 0, 0)
		i += 1

	if len(command) > 0:
		ser.write(command)

	time.sleep(2)
	
