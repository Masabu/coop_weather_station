
import time
import random
import urequests
from machine import Pin
from time import sleep
import onewire
import ds18x20
from secret import BLYNK_AUTH_TOKEN

print(f"{BLYNK_AUTH_TOKEN}")

class Monitor:
    def __init__(self, ds_pin, AUTH):

        # Setup DS18B20
        self.ds_pin = ds_pin
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.roms = self.ds_sensor.scan()
        print(f'Found {len(self.roms)} sensor(s)')

        # Blynk configuration
        self.BLYNK_AUTH = AUTH
        self.BLYNK_URL = "https://blynk.cloud/external/api/batch/update"

    def send_to_blynk(self, sensor1_temp, sensor2_temp):
        """Send both sensor readings in one API call"""
        try:
            query = (
                f"?token={self.BLYNK_AUTH}"
                f"&V0={sensor1_temp}"
                f"&V1={sensor2_temp}"
            )
            url = self.BLYNK_URL + query
            response = urequests.get(url)
            print(f'Blynk response: {response.status_code}')
            print(f"URL sent: {url}")
            response.close()
            return True
        except Exception as e:
            print(f'Error sending to Blynk: {e}')
            return False

    def read_humidity(self):
        """Placeholder for humidity sensor reading"""
        # TODO: Implement humidity sensor reading
        pass

    def set_led_status(self, status):
        """Placeholder for LED status indicator"""
        # TODO: Implement LED status control
        pass

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
                self.send_to_blynk(temp1, temp2)

            # Placeholder: read humidity
            self.read_humidity()

            # Placeholder: set LED status
            self.set_led_status("ok")

            sleep(wait_time)  # Wait before the next reading


if __name__ == "__main__":
    monitor = Monitor(ds_pin=5, AUTH=BLYNK_AUTH_TOKEN)
    monitor.loop_section(wait_time=258)






