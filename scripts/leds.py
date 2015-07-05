import serial, time, math
from struct import *

class Color:
	def __init__(self, r = 0, g = 0, b = 0, hue = None):
		if hue != None:
			self.to_rgb(hue, 1, 1);
		else:
			self.r = r
			self.g = g
			self.b = b
	
	def __str__(self):
		return '( ' + str(self.r) + ', ' +str(self.g) + ', ' +str(self.b) + ' )'
	
	def to_rgb(self, hue, saturation, value):
		hueIndex = int(math.floor(hue / 60.0)) % 6
    
		f = (hue / 60.0) - hueIndex
		p = value * (1.0 - saturation)
		q = value * (1.0 - f * saturation)
		t = value * (1.0 - (1.0 - f) * saturation)

		if hueIndex == 0:
			r = value
			g = t
			b = p
		elif hueIndex == 1:
			r = q
			g = value
			b = p;
		elif hueIndex == 2:
			r = p
			g = value
			b = t
		elif hueIndex == 3:
			r = p
			g = q
			b = value
		elif hueIndex == 4:
			r = t
			g = p
			b = value
		elif hueIndex == 5:
			r = value
			g = p
			b = q
		
		self.r = int(255.0 * r)
		self.g = int(255.0 * g)
		self.b = int(255.0 * b)

class LedController:
	LED_CONTROLLER_FADE = 0
	LED_CONTROLLER_BLINK = 1
	LED_CONTROLLER_CONSTANT = 2
	LED_CONTROLLER_LED_COUNT = 12

	LED_DEFAULT_BAUDRATE = 9600
	LED_DEFAULT_DEVICE = "/dev/ttyUSB1"

	def __init__ (self, device = LED_DEFAULT_DEVICE, baudrate = LED_DEFAULT_BAUDRATE):
		self.serial = serial.Serial(device, baudrate)
		self.temp = 0
		# The arduino take some times to boot after reset, let it cool
		time.sleep(2)

	def send(self, command):
		self.serial.write(command)
		self.serial.flush()

	def send_command(self, led, type, color):
		self.send(pack('!BBBBBB', 0, led, type, color.r, color.g, color.b))

	def set_led_fade(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_FADE,color)

	def set_led_blink(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_BLINK,color)

	def set_led_constant(self, led, color):
		self.send_command(led, self.LED_CONTROLLER_CONSTANT,color)

	def get_temp(self):
		self.send(pack('!B', 1))
		# We expect to receive a float
		temp_bytes = self.serial.read(4)
		self.temp = unpack('f', temp_bytes)[0] - 2
		return self.temp

	def reset(self):
		for led in range(0, self.LED_CONTROLLER_LED_COUNT):
			self.set_led_constant(led, Color(0, 0, 0))
			
	def get_led_count(self):
		return self.LED_CONTROLLER_LED_COUNT


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


