#ifndef LED_CTRL_H
#define LED_CTRL_H

enum led_ctrl_state {
	LED_CTRL_FADE = 0,
	LED_CTRL_BLINK,
	LED_CTRL_CONSTANT,
};

typedef struct led_ctrl_state_set {
	uint8_t led;
	uint8_t state;
	uint8_t r, g, b;
} led_ctrl_state_set_t __attribute__((packed));

#endif
