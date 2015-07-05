#!/usr/bin/python

import requests, json, sys, time, serial
from leds import *

class JenkinsJob:
	JENKINS_API_JSON = '/api/json'
	JENKINS_BASE_URL = 'https://localhost:8443/jenkins/job/'

	def __init__(self, job_name):
		self.job_url = self.JENKINS_BASE_URL + job_name + "/"
		self.build_number = 0

	def refresh(self, build_id):
		try:
			r = requests.get(self.job_url + build_id + self.JENKINS_API_JSON, verify=False)
			self.job_status = r.json()
		except requests.exceptions.ConnectionError:
			print 'Fail to connect to jenkins instance: ' + self.JENKINS_BASE_URL
			exit(1)
			

	def is_new_build(self):
		if self.job_status['number'] != self.build_number:
			self.build_number = self.job_status['number']
			return True

		return False

	def is_user_build(self, username):
		actions = self.job_status['actions']
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


class JenkinsJobLeds:
	BUILDING_COLOR = Color(0, 0, 255)
	SUCCESS_COLOR = Color(0, 0, 255)
	USER_FAILURE_COLOR = Color(255, 0, 0)
	USER_COLOR = Color(0, 255, 0)
	UNSTABLE_COLOR = Color(229, 198, 0)
	FAILURE_COLOR = Color(255, 0, 0)

	def __init__(self, job, leds, username):
		self.job = job
		self.leds = leds
		self.job_failed = False;
		self.leds.reset();
		self.username = username

	def refresh(self):
		self.job.refresh('lastBuild')

		user_build = self.job.is_user_build(self.username)

		if self.job.is_new_build():
			self.leds.reset()

		i = 0
		for build in self.job.job_status['subBuilds']:
			if build['result'] == 'SUCCESS':
				self.leds.set_led_constant(i, self.SUCCESS_COLOR)
			if build['result'] == 'UNSTABLE':
				self.leds.set_led_constant(i, self.UNSTABLE_COLOR)
			if build['result'] == None:
				if user_build:
					self.leds.set_led_fade(i, self.USER_COLOR)
				else:
					self.leds.set_led_fade(i, self.BUILDING_COLOR)
			if build['result'] == 'FAILURE':
				if user_build:
					self.leds.set_led_fade(i, self.USER_FAILURE_COLOR)
				else:
					self.leds.set_led_constant(i, self.FAILURE_COLOR)
			i += 1


def main():
	
	username = sys.argv[3]

	print 'Checking for user jobs for ' + username

	leds = LedController()

	job1 = JenkinsJobLeds(JenkinsJob(sys.argv[1]), SubLedController(leds, 0, 6, False), username)
	job2 = JenkinsJobLeds(JenkinsJob(sys.argv[2]), SubLedController(leds, 6, 6, True), username)

	try:
		while True:
			job1.refresh()
			job2.refresh()
			time.sleep(2)

	except KeyboardInterrupt:
		leds.reset()


if __name__ == "__main__":

	if len(sys.argv) < 3:
		print 'Missing job name and username'
		exit(1)

	main()
