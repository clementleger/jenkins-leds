#ifndef LED_CTRL_H
#define LED_CTRL_H

enum led_ctrl_state {
	LED_CTRL_FADE = 0,
	LED_CTRL_BLINK,
	LED_CTRL_CONSTANT,
};

typedef struct led_ctrl_state_blink {
	uint16_t on_duration;
	uint16_t off_duration;
} led_ctrl_state_blink_t __attribute__((packed));

typedef struct led_ctrl_state_fade {
	uint16_t rate_per_sec;
} led_ctrl_state_fade_t __attribute__((packed));

typedef struct led_ctrl_state_set {
	uint8_t led;
	uint8_t state;
	uint8_t r, g, b;
} led_ctrl_state_set_t __attribute__((packed));

#endif
