#!/usr/bin/python

import requests, json, sys, time, serial

url_base = "https://localhost:8443/jenkins/job/"

if len(sys.argv) < 2:
	print "Missing Job name"
	exit(1)

url = url_base + sys.argv[1] + "/lastBuild/api/json"

ser = serial.Serial('/dev/ttyUSB1', 9600)

time.sleep(3)
for i in range(0,5):
	command = str(i) + "0"
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
			command += str(i) + "2"
		if build['result'] == None:
			command += str(i) + "1"
		if build['result'] == 'FAILURE':
			command += str(i) + "3"
		i += 1

	if len(command) > 0:
		ser.write(command)

	time.sleep(2)
	
