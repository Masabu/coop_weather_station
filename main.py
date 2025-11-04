import network
import time
import machine
from secret import BLYNK_AUTH_TOKEN, SSID2, PASSWORD, SSID1
from utilities import Led_Toggle, led_blink, connect_wifi
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

time.sleep(5)

try:
    ntptime.settime()  # Sets the RTC to UTC from NTP
    print("NTP time sync successful")
    log['ntp_sync'] = True
except Exception as e:
    print("NTP sync failed:", e)
    log['ntp_sync'] = False

from monitor import Monitor

probe = Monitor(AUTH=BLYNK_AUTH_TOKEN)

log['bme_connected'] = probe.bme_init
log['bme_address'] = probe.bme_addr if log['bme_connected'] else None
log['ds18b20_sensors'] = len(probe.roms)
log['ds18b20_connected'] = probe.ds_sensor_init

print("Initialization log:", log)

probe.loop_section(wait_time=180)



