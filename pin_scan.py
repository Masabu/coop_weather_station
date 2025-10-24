from machine import Pin
from time import sleep

pin_num = 1  # Change this to test other GPIOs
led = Pin(pin_num, Pin.OUT)

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)

