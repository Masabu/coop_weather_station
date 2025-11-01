## utilities.py

from time import sleep
from machine import Pin

def Led_Toggle(pin_num, status):
    led = Pin(pin_num, Pin.OUT)
    if status == "ON":
        led.on()
    elif status == "OFF":
        led.off()
    else:
        print("Invalid status. Use 'ON' or 'OFF'.")

def led_blink(pin_num=23, times=5, interval=0.2):
    led = Pin(pin_num, Pin.OUT)
    for _ in range(times):
        led.on()
        sleep(interval)
        led.off()
        sleep(interval)

