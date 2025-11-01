import network
import time
from secret import BLYNK_AUTH_TOKEN, SSID, PASSWORD
from utilities import Led_Toggle

'''
itialize LED to OFF state

Led_Toggle(2, "OFF") # green light at D2 Pin2 : wifi status
Led_Toggle(22, "OFF") # yellow light at D22 Pin22 : sensor status
Led_Toggle(23, "OFF") # red light at D23 Pin23 : data transmission status
Led_Toggle(27, "OFF") # blue light at D27 Pin27: BME 280 sensor status

'''

i = 0
LEDs = [2,22,23,27]
while i <8:
    for l in LEDs:
        Led_Toggle(l, "ON")
        time.sleep(.1)
        Led_Toggle(l, "OFF")
    i +=1

## Turn on WIFI
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to SSID:", SSID)
wlan.connect(SSID, PASSWORD)
for _ in range(10):
    print("Connected?", wlan.isconnected())
    time.sleep(1)
if wlan.isconnected():
    Led_Toggle(2, "ON") # green light at D4 Pin4


from monitor import Monitor

probe = Monitor(AUTH=BLYNK_AUTH_TOKEN)
probe.loop_section(wait_time=100)

