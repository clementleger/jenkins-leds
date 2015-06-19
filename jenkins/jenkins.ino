// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library

#include <Adafruit_NeoPixel.h>

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1
#define PIN            6

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS      5

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);


#define JENKINS_DEFAULT         0
#define JENKINS_BUILDING        1
#define JENKINS_SUCCESS         2
#define JENKINS_FAILURE		3
#define JENKINS_COUNT		4

uint8_t leds_status[NUMPIXELS] = {JENKINS_SUCCESS, JENKINS_FAILURE, JENKINS_SUCCESS, JENKINS_FAILURE, JENKINS_SUCCESS};

static void setup_led (int led, uint8_t status)
{
	uint32_t color;

	leds_status[led] = status;
	switch (leds_status[led]) {
		case JENKINS_DEFAULT:
			color = pixels.Color(0, 0, 0);
			break;
		case JENKINS_SUCCESS:
			color = pixels.Color(0, 150, 0);
			break;
		case JENKINS_FAILURE:
			color = pixels.Color(150, 0, 0);
			break;
		default:
			return;
        }
	pixels.setPixelColor(led, color);
}

static float loop_count = 0;

void setup() {

	Serial.begin(9600);
	pixels.begin(); // This initializes the NeoPixel library.
  
	for (int i = 0; i < NUMPIXELS; i++)
		setup_led (i, leds_status[i]);

	pixels.setBrightness(70);
}

int check_serial()
{
        uint8_t led, state;

        if (Serial.available() >= 2) {
		led = Serial.read();
		led -= '0';
		if (led >= NUMPIXELS)
			return 0;
		state = Serial.read();
		state -= '0';
		if (state >= JENKINS_COUNT)
			return 0;

		setup_led (led, state);
		return 1;
	}
}

void loop() {
        uint8_t blink;
        bool update = false;
        for(int i = 0; i < NUMPIXELS; i++){
                if (leds_status[i] == JENKINS_BUILDING) {
                        blink = fabs(sin(loop_count)) * 255;

                        pixels.setPixelColor(i, pixels.Color(0, 0, blink));
                        update = true;
                }
        }
	
	if (check_serial())
		update = true;
        
        loop_count += 0.02;
        if (update)
                pixels.show();

        delay(10);
}
