from machine import Pin
from time import sleep

pin_num = 3
led = Pin(pin_num, Pin.OUT)

j = 0
while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
    j += 1
    if j >= 10:
        break





