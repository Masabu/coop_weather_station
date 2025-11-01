# Wiring Guide: Chicken Coop Weather Station

## Overview
This guide summarizes the wiring for all sensors and indicators in the project, including pin assignments, resistor values, and recommended practices for ESP32-based builds.

---

## GPIO Pin Assignments

| GPIO Pin | Function                  | Device/Color         |
|----------|---------------------------|----------------------|
| 4        | WiFi status LED           | Green                |
| 22       | Sensor status LED         | Yellow               |
| 23       | Data transmission LED     | Red                  |
| 27       | I2C/BME280 status LED     | Blue                 |
| 5        | DS18B20 1-Wire bus        | Temp sensors         |
| 25       | I2C SDA                   | BME280 (SDA)         |
| 26       | I2C SCL                   | BME280 (SCL)         |

---

## LED Wiring
- **Each LED:**
  - Connect the GPIO pin to one end of a 220 Ω resistor.
  - Connect the other end of the resistor to the LED anode (long leg).
  - Connect the LED cathode (short leg) to GND.
  - (You may swap resistor and LED order; both work as long as they are in series.)
- **One resistor per LED.**

```
GPIOx ── 220Ω ──▶|── GND
             LED
```

---

## DS18B20 (1-Wire) Wiring
- **Data:** Connect all DS18B20 data pins to GPIO5.
- **Power:** Connect VDD to 3.3V, GND to GND.
- **Pull-up resistor:** Place a 4.7 kΩ resistor between DATA (GPIO5) and 3.3V. Only one pull-up is needed for the whole bus.

```
3.3V ──┬─────────────┬─────────────┐
       │             │             │
     [4.7k]        DS18B20      DS18B20
       │             │             │
GPIO5──┴──── DATA ---┴---- DATA ---┘
GND ────────────────┴──────────────┘
```

---

## BME280 I2C Wiring
- **SDA:** Connect ESP32 GPIO25 to BME280 SDA.
- **SCL:** Connect ESP32 GPIO26 to BME280 SCL.
- **VCC:** Connect BME280 VCC to 3.3V (not 5V!).
- **GND:** Connect BME280 GND to ESP32 GND.
- **I2C Pull-ups:** Most BME280 modules include onboard pull-ups. If not, add 4.7 kΩ resistors from SDA and SCL to 3.3V.
- **Address:** Default is 0x76 or 0x77 (check your module or scan with i2c.scan()).

```
ESP32         BME280
=====         ======
GPIO25 ────── SDA
GPIO26 ────── SCL
3.3V   ────── VCC
GND    ────── GND
```

---

## Additional Notes
- Avoid using ESP32 pins 6–11 (flash), 34–39 (input only), and be careful with boot/strap pins (0, 2, 12, 15).
- Use a separate resistor for each LED.
- If you add more sensors or actuators, update this guide and check for pin conflicts.

---

For more details, see the main `README.md`.
