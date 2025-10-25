## utilities.py

from machine import Pin

def Led_Toggle(pin_num, status):
    led = Pin(pin_num, Pin.OUT)
    if status == "ON":
        led.on()
    elif status == "OFF":
        led.off()
    else:
        print("Invalid status. Use 'ON' or 'OFF'.")
