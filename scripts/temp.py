#!/usr/bin/python
import serial, time
from leds import *

class TempMonitor:
	MIN_TEMP_COLOR_HSV = 185
	MIN_TEMP = 18
	MAX_TEMP = 32

	def __init__(self, leds):
		self.leds = leds

	def refresh(self):
		temp = self.leds.get_temp()
		print 'temperature: ' + str(temp)
		if temp < self.MIN_TEMP:
			temp = self.MIN_TEMP
		if temp > self.MAX_TEMP:
			temp = self.MAX_TEMP
		
		hue_color = (self.MAX_TEMP - temp) * self.MIN_TEMP_COLOR_HSV / (self.MAX_TEMP - self.MIN_TEMP)
		
		for led in range (0, self.leds.get_led_count()):
			self.leds.set_led_constant(led, Color(hue = hue_color))
			
		return temp
		
def main():
	
	leds = LedController()
	temp_mon = TempMonitor(leds)

	try:
		while True:
			temp_mon.refresh()
			time.sleep(10)

	except KeyboardInterrupt:
		leds.reset()


if __name__ == "__main__":
	main()
