#include <Adafruit_NeoPixel.h>
#include "./led_ctrl.h"

#define PIN            6
#define NUMPIXELS      12

#define SIN_STEPS	40
#define STEP_INCREMENT	((float) 1/(float)SIN_STEPS)

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ400);

struct led_state{
	uint8_t r, g, b;
	uint8_t state;
};

struct led_state leds[NUMPIXELS] = {0};

void setup_led(led_ctrl_state_set_t state_set)
{
	uint32_t color;
	uint8_t led = state_set.led;

	leds[led].state = state_set.state;
	leds[led].r = state_set.r;
	leds[led].g = state_set.g;
	leds[led].b = state_set.b;

	if (state_set.state == LED_CTRL_CONSTANT) {
		pixels.setPixelColor(led, pixels.Color(state_set.r, state_set.g, state_set.b));
	}
}

int check_serial()
{
	led_ctrl_state_set_t state;

        if (Serial.available() >= sizeof(led_ctrl_state_set_t)) {
		Serial.readBytes((char *) &state, sizeof(led_ctrl_state_set_t));

		setup_led (state);
		return 1;
	}
	
	return 0;
}

static unsigned long blink_update_millis = 0;
static unsigned long fade_update_millis = 0;
static float loop_count = 0;
static bool blink_state = false;

void setup()
{
	Serial.begin(9600);
	pixels.begin();
	pixels.setBrightness(50);
}

void loop()
{
        uint8_t r,g,b;
	uint32_t color;
        bool update = false, blink_update = false, fade_update = false;
	float prop;
	unsigned long current_millis = millis();
	
	if ((current_millis - blink_update_millis) >= 500) {
		blink_update_millis = current_millis;
		blink_state = !blink_state;
		blink_update = true;
	}
	
	if ((current_millis - fade_update_millis) >= 10) {
		fade_update_millis = current_millis;
		fade_update = true;
		loop_count += STEP_INCREMENT;
	}

        for(int i = 0; i < NUMPIXELS; i++){
                if (leds[i].state == LED_CTRL_FADE && fade_update) {
			prop = fabs(sin(loop_count));
                        r = prop * leds[i].r;
                        g = prop * leds[i].g;
                        b = prop * leds[i].b;

                        pixels.setPixelColor(i, pixels.Color(r, g, b));
                        update = true;
                }
		if (leds[i].state == LED_CTRL_BLINK && blink_update) {
			if (blink_state == true) {
				color = pixels.Color(leds[i].r, leds[i].g, leds[i].b);
			} else {
				color = 0;
			}
			pixels.setPixelColor(i, color);
			update = true;
		}
        }

	if (check_serial())
		update = true;

        if (update)
                pixels.show();
}
