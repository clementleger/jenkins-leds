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

enum led_ctrl_msg_type {
	LED_CTRL_STATE_SET = 0,
	LED_CTRL_TEMP_GET,
};

typedef struct led_ctrl_msg {
	uint8_t type;
} led_ctrl_msg_t;

typedef struct led_ctrl_msg_temp {
	float temp;
} led_ctrl_msg_temp_t;

#endif
