import network
import time

def connect_wifi(ssid_list, password_list, max_attempts=10, log=None):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for ssid, password in zip(ssid_list, password_list):
        print("Trying SSID:", ssid)
        wlan.disconnect()
        wlan.connect(ssid, password)
        for attempt in range(max_attempts):
            print(f"Connection attempt {attempt + 1}")
            if wlan.isconnected():
                print("Connected to", ssid)
                print("IP:", wlan.ifconfig()[0])
                if log is not None:
                    log['ip'] = wlan.ifconfig()[0]
                    log['ssid'] = ssid
                    log['attempts'] = attempt + 1
                return True
            time.sleep(1)
        print("Failed to connect to", ssid)
    print("All SSIDs failed.")
    if log is not None:
        log['ip'] = None
        log['ssid'] = None
        log['attempts'] = max_attempts * len(ssid_list)
    return False
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


import urequests
import json


class Weather:
    def __init__(self, latitude, longitude, timezone="America/Chicago", forecast_days=3):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.forecast_days = forecast_days

    def get_weather_forecast(self):
        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "timezone": self.timezone,
            "forecast_days": self.forecast_days
        }
        url = base_url + "?"
        for key, value in params.items():
            url += f"{key}={value}&"
        url = url[:-1]
        print("Fetching weather data...")
        response = urequests.get(url)
        data = json.loads(response.text)
        response.close()
        return data

    @staticmethod
    def weather_code_to_condition(code):
        label_id = {
            'sunny': 0,
            'partly cloudy': 1,
            'cloudy': 2,
            'drizzle': 3,
            'rain': 4,
            'heavy rain': 5,
            'snow': 6,
            'thunderstorm': 7,
            'hail': 8,
            'unknown': 9
        }
        mapping = {
            0: 'sunny', 1: 'sunny', 2: 'partly cloudy', 3: 'cloudy', 45: 'cloudy', 48: 'cloudy',
            51: 'drizzle', 53: 'drizzle', 55: 'drizzle', 61: 'rain', 63: 'rain', 65: 'heavy rain',
            71: 'snow', 73: 'snow', 75: 'snow', 77: 'snow', 80: 'rain', 81: 'rain', 82: 'heavy rain',
            85: 'snow', 86: 'snow', 95: 'thunderstorm', 99: "hail"
        }
        return mapping.get(code, 'unknown'), label_id.get(mapping.get(code, 'unknown'), 9)

    @staticmethod
    def send_weather_summary_to_blynk(monitor, weather_summary):
        def strip_year(date_str):
            return date_str.replace('2025-', '')
        data = {
            'V8': weather_summary[0]['code'],
            'V9': weather_summary[1]['code'],
            'V10': weather_summary[2]['code'],
            'V5': f'"{strip_year(weather_summary[0]["date"])}:{weather_summary[0]["min"]}/{weather_summary[0]["max"]}"',
            'V6': f'"{strip_year(weather_summary[1]["date"])}:{weather_summary[1]["min"]}/{weather_summary[1]["max"]}"',
            'V7': f'"{strip_year(weather_summary[2]["date"])}:{weather_summary[2]["min"]}/{weather_summary[2]["max"]}"'
        }
        monitor.send_to_blynk(data)

    @staticmethod
    def print_daily_forecast(weather_data):
        print("\n" + "="*50)
        print("7-DAY WEATHER FORECAST")
        print("="*50)
        daily = weather_data['daily']
        for i in range(3):
            print(f"\nDay {i+1}: {daily['time'][i]}")
            print("-" * 40)
            cond_label, cond_id = Weather.weather_code_to_condition(daily['weather_code'][i])
            print(f"  Condition: {cond_label} (id={cond_id})")
            print(f"  Temperature: {daily['temperature_2m_min'][i]}°C - {daily['temperature_2m_max'][i]}°C")
            print(f"  Rain Chance: {daily['precipitation_probability_max'][i]}%")

