#include <Adafruit_NeoPixel.h>
#include "./led_ctrl.h"

#define PIN            6
#define NUMPIXELS      6

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ400);

struct led_state{
	uint8_t r, g, b;
	uint8_t state;
	union {
		led_ctrl_state_blink_t blink;
		led_ctrl_state_fade_t fade;
	};
};

struct led_state leds_state[NUMPIXELS] = {0};

void setup_led(led_ctrl_state_set_t state_set)
{
	uint32_t color;
	uint8_t led = state_set.led;
	Serial.print("Got set for led");
	Serial.println(led);

	leds_state[led].state = state_set.state;
	leds_state[led].r = state_set.r;
	leds_state[led].g = state_set.g;
	leds_state[led].b = state_set.b;
	
	if (state_set.state == LED_CTRL_FADE)
		Serial.readBytes((char *) &leds_state[led].fade, sizeof(led_ctrl_state_fade_t));
	else if (state_set.state == LED_CTRL_BLINK)
		Serial.readBytes((char *) &leds_state[led].blink, sizeof(led_ctrl_state_blink_t));
	else
		pixels.setPixelColor(led, pixels.Color(state_set.r, state_set.g, state_set.b));
	
}

int check_serial()
{
	led_ctrl_state_set_t state;

        if (Serial.available() >= sizeof(led_ctrl_state_set_t)) {
		Serial.readBytes((char *) &state, sizeof(led_ctrl_state_set_t));

		setup_led (state);
		return 1;
	}
}

static float loop_count = 0;

void setup() {

	Serial.begin(9600);
	pixels.begin(); // This initializes the NeoPixel library.
	pixels.setBrightness(70);
}

void loop() {
        uint8_t r,g,b;
        bool update = false;

        for(int i = 0; i < NUMPIXELS; i++){
                if (leds_state[i].state == LED_CTRL_FADE) {
                        r = fabs(sin(loop_count)) * leds_state[i].r;
                        g = fabs(sin(loop_count)) * leds_state[i].g;
                        b = fabs(sin(loop_count)) * leds_state[i].b;

                        pixels.setPixelColor(i, pixels.Color(r, g, b));
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
