
import time
import random
import urequests
from time import sleep
import onewire
import ds18x20
from utilities import Led_Toggle
from machine import Pin

class Monitor:
    def __init__(self, ds_pin, AUTH):

        # Setup DS18B20
        self.ds_pin = ds_pin
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.roms = self.ds_sensor.scan()
        print(f'Found {len(self.roms)} sensor(s)')

        if len(self.roms) == 2:
            print("2 DS18B20 sensors found!")
            Led_Toggle(22, "ON") # orange light at D22 Pin22

        # Blynk configuration
        self.BLYNK_AUTH = AUTH
        self.BLYNK_URL = "http://blynk.cloud/external/api/batch/update"


    def send_to_blynk(self, sensor1_temp, sensor2_temp):
        """Send both sensor readings in one API call"""
        try:
            query = (
                f"?token={self.BLYNK_AUTH}"
                f"&V0={sensor1_temp}"
                f"&V1={sensor2_temp}"
            )
            self.url = self.BLYNK_URL + query
            response = urequests.get(self.url)
            print(f'Blynk response: {response.status_code}')
            print(f"URL sent: {self.url}")
            response.close()
            return True
        except Exception as e:
            print(f'Error sending to Blynk: {e}')
            return False

    def read_humidity(self):
        """Placeholder for humidity sensor reading"""
        # TODO: Implement humidity sensor reading
        pass

    def led_blink(self, pin_num=23, times=3, interval=0.2):
        led = Pin(pin_num, Pin.OUT)
        for _ in range(times):
            led.on()
            sleep(interval)
            led.off()
            sleep(interval)

    def loop_section(self, wait_time=30):
        while True:
            # Read temperatures
            self.ds_sensor.convert_temp()
            sleep(0.75)

            if len(self.roms) >= 2:
                temp1 = self.ds_sensor.read_temp(self.roms[0])
                temp2 = self.ds_sensor.read_temp(self.roms[1])

                print(f'Sensor 1: {temp1}°C')
                print(f'Sensor 2: {temp2}°C')

                # Send both readings in ONE API call
                if self.send_to_blynk(temp1, temp2):
                    self.led_blink(pin_num=23, times=10, interval=1)                
        

            # Placeholder: read humidity
            self.read_humidity()

            sleep(wait_time)  # Wait before the next reading


if __name__ == "__main__":
    monitor = Monitor(ds_pin=5, AUTH=BLYNK_AUTH_TOKEN)
    monitor.loop_section(wait_time=258)






