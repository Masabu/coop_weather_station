import network
import time
import machine
from secret import BLYNK_AUTH_TOKEN, SSID2, PASSWORD, SSID1
from utilities import Led_Toggle, led_blink, connect_wifi, sync_time_chicago
### set time
import ntptime


i = 0
LEDs = [2,22,23,27]
while i <8:
    for l in LEDs:
        Led_Toggle(l, "ON")
        time.sleep(.1)
        Led_Toggle(l, "OFF")
    i +=1

log = {}

# Usage:
connect_wifi([SSID1, SSID2], [PASSWORD, PASSWORD], log=log)

time.sleep(5)  # give some time before syncing time
sync_time_chicago(log)

from monitor import Monitor

probe = Monitor(AUTH=BLYNK_AUTH_TOKEN, log=log)
print("Initialization log:", probe.log)
probe.loop_section(wait_time=60)


