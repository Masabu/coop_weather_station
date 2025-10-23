import network
import time
from secret import SSID, PASSWORD

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to SSID:", SSID)
wlan.connect(SSID, PASSWORD)
for _ in range(15):
    print("Connected?", wlan.isconnected())
    time.sleep(1)

print("Final config:", wlan.ifconfig())

# Run monitor.py after WiFi connection
from monitor import Monitor
from secret import BLYNK_AUTH_TOKEN
from machine import Pin

monitor = Monitor(ds_pin=Pin(5), AUTH=BLYNK_AUTH_TOKEN)
monitor.loop_section(258)



