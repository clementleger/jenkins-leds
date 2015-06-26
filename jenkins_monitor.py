#!/usr/bin/python

import requests, json, sys, time, serial
from struct import *

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b


class LedController:
	LED_CONTROLLER_FADE = 0
	LED_CONTROLLER_BLINK = 1
	LED_CONTROLLER_CONSTANT = 2
	LED_CONTROLLER_LED_COUNT = 12

	LED_DEFAULT_BAUDRATE = 9600
	LED_DEFAULT_DEVICE = "/dev/ttyUSB0"

	def __init__ (self, device = LED_DEFAULT_DEVICE, baudrate = LED_DEFAULT_BAUDRATE):
		self.serial = serial.Serial(device, baudrate)
		# The arduino take some times to boot after reset, let it cool
		time.sleep(2)

	def send(self, command):
		self.serial.write(command)
		self.serial.flush()

	def send_command(self, led, type, color):
		self.send(pack('!BBBBB', led, type, color.r, color.g, color.b))

	def set_led_fade(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_FADE,color)

	def set_led_blink(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_BLINK,color)

	def set_led_constant(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_CONSTANT,color)

	def reset(self):
		for led in range(0, self.LED_CONTROLLER_LED_COUNT):
			self.set_led_constant(led, Color(0, 0, 0))


class SubLedController:
	def __init__(self, leds, led_offset, led_count, inverted):
		self.leds = leds
		self.led_offset = led_offset
		self.led_count = led_count
		self.inverted = inverted

	def led_id(self, led):
		if self.inverted:
			return self.led_count + self.led_offset - led - 1

		return self.led_offset + led

	def set_led_constant(self, led, color):
		self.leds.set_led_constant(self.led_id(led), color)

	def set_led_blink(self, led, color):
		self.leds.set_led_blink(self.led_id(led), color)

	def set_led_fade(self, led, color):
		self.leds.set_led_fade(self.led_id(led), color)

	def reset(self):
		for led in range(0, self.led_count):
			self.set_led_constant(led, Color(0, 0, 0))


class JenkinsJob:
	JENKINS_API_JSON = '/api/json'
	JENKINS_BASE_URL = 'https://hudson.kalray.eu:8443/jenkins/job/'

	def __init__(self, job_name):
		self.job_url = self.JENKINS_BASE_URL + job_name + "/"
		self.build_number = 0

	def refresh(self, build_id):
		r = requests.get(self.job_url + build_id + self.JENKINS_API_JSON, verify=False)
		self.job_status = r.json()

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
