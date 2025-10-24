import network
import time
from secret import SSID, PASSWORD

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to SSID:", SSID)
wlan.connect(SSID, PASSWORD)
for _ in range(10):
    print("Connected?", wlan.isconnected())
    time.sleep(1)

print("Final config:", wlan.ifconfig())


# Run monitor.py after WiFi connection
from monitor import Monitor
from secret import BLYNK_AUTH_TOKEN
from machine import Pin

monitor = Monitor(ds_pin=Pin(5), AUTH=BLYNK_AUTH_TOKEN)

print("Testing Morse Code on Pin 1")
for i in range(10):
    print(f"Sending Morse code for: {i}")
    monitor.send_morse_code(str(i), 1, dot_time=0.2)
    time.sleep(2)



## send readings every 258 seconds
monitor.loop_section(258)

