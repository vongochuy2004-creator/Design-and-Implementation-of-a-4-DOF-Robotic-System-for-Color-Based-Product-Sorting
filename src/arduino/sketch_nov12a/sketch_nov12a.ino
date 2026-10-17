#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define NUM_LEDS 8

Adafruit_NeoPixel strip(
  NUM_LEDS,
  LED_PIN,
  NEO_GRB + NEO_KHZ800
);

void setup() {
  strip.begin();
  strip.show();
}

void loop() {

  for (int i = 0; i < NUM_LEDS; i++) {

    // LED hiện tại sáng
    strip.setPixelColor(i, strip.Color(155, 0, 0));

    // Các LED phía sau tạo đuôi mờ
    if (i > 0)
      strip.setPixelColor(i - 1, strip.Color(100, 40, 0));

    if (i > 1)
      strip.setPixelColor(i - 2, strip.Color(30, 10, 0));

    if (i > 2)
      strip.setPixelColor(i - 3, strip.Color(5, 2, 0));

    strip.show();
    delay(100);
  }
}