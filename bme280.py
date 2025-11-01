# BME280 MicroPython Library
# Supports both I2C and SPI interfaces
# Compatible with ESP32 and other MicroPython boards

from micropython import const
from ustruct import unpack, unpack_from
from array import array

# BME280 default I2C address
BME280_I2CADDR = 0x76  # Alternative: 0x77

# Operating Modes
MODE_SLEEP = const(0)
MODE_FORCED = const(1)
MODE_NORMAL = const(3)

# Oversampling options
OVERSCAN_X1 = const(1)
OVERSCAN_X2 = const(2)
OVERSCAN_X4 = const(3)
OVERSCAN_X8 = const(4)
OVERSCAN_X16 = const(5)

# Standby time constants
STANDBY_0_5 = const(0)
STANDBY_62_5 = const(1)
STANDBY_125 = const(2)
STANDBY_250 = const(3)
STANDBY_500 = const(4)
STANDBY_1000 = const(5)
STANDBY_10 = const(6)
STANDBY_20 = const(7)

# Filter coefficients
FILTER_OFF = const(0)
FILTER_2 = const(1)
FILTER_4 = const(2)
FILTER_8 = const(3)
FILTER_16 = const(4)


class BME280:
    """Base class for BME280 sensor"""
    
    def __init__(self, mode=MODE_NORMAL, 
                 oversample_t=OVERSCAN_X2,
                 oversample_p=OVERSCAN_X16,
                 oversample_h=OVERSCAN_X1,
                 standby=STANDBY_250,
                 filter=FILTER_OFF):
        
        self.mode = mode
        self.oversample_t = oversample_t
        self.oversample_p = oversample_p
        self.oversample_h = oversample_h
        self.standby = standby
        self.filter = filter
        
        # Load calibration data from sensor
        dig_88_a1 = self.read(0x88, 26)
        dig_e1_e7 = self.read(0xE1, 7)
        
        self.dig_T1, self.dig_T2, self.dig_T3, self.dig_P1, \
            self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, \
            self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9, \
            _, self.dig_H1 = unpack("<HhhHhhhhhhhhBB", dig_88_a1)
        
        self.dig_H2, self.dig_H3 = unpack("<hB", dig_e1_e7)
        e4_sign = unpack_from("<b", dig_e1_e7, 3)[0]
        self.dig_H4 = (e4_sign << 4) | (dig_e1_e7[4] & 0xF)
        
        e6_sign = unpack_from("<b", dig_e1_e7, 5)[0]
        self.dig_H5 = (e6_sign << 4) | (dig_e1_e7[4] >> 4)
        
        self.dig_H6 = unpack_from("<b", dig_e1_e7, 6)[0]
        
        # Configure sensor
        self.write(0xF2, self.oversample_h)
        self.write(0xF4, (self.oversample_t << 5 | self.oversample_p << 2 | self.mode))
        self.write(0xF5, (self.standby << 5 | self.filter << 2))
        
        self.t_fine = 0
    
    def read(self, addr, n_bytes):
        """Read bytes from sensor - implemented by subclass"""
        raise NotImplementedError
    
    def write(self, addr, byte):
        """Write byte to sensor - implemented by subclass"""
        raise NotImplementedError
    
    @property
    def temperature(self):
        """Read temperature in Celsius"""
        raw = self.read(0xFA, 3)
        adc_T = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        
        var1 = ((adc_T / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2)
        var2 = ((adc_T / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        self.t_fine = int(var1 + var2)
        
        return self.t_fine / 5120.0
    
    @property
    def pressure(self):
        """Read pressure in hPa (hectopascals)"""
        temp = self.temperature  # Must read temperature first to update t_fine
        raw = self.read(0xF7, 3)
        adc_P = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        
        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        
        if var1 == 0:
            return 0
        
        p = 1048576.0 - adc_P
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = self.dig_P9 * p * p / 2147483648.0
        var2 = p * self.dig_P8 / 32768.0
        p = p + (var1 + var2 + self.dig_P7) / 16.0
        
        return p / 100.0  # Convert Pa to hPa
    
    @property
    def humidity(self):
        """Read relative humidity in %"""
        temp = self.temperature  # Must read temperature first to update t_fine
        raw = self.read(0xFD, 2)
        adc_H = (raw[0] << 8) | raw[1]
        
        h = self.t_fine - 76800.0
        h = ((adc_H - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * h)) *
             (self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * h *
             (1.0 + self.dig_H3 / 67108864.0 * h))))
        h = h * (1.0 - self.dig_H1 * h / 524288.0)
        
        if h > 100:
            h = 100
        elif h < 0:
            h = 0
        
        return h
    
    @property
    def values(self):
        """Read all sensor values at once
        Returns: (temperature, pressure, humidity)
        """
        return (self.temperature, self.pressure, self.humidity)


class BME280_I2C(BME280):
    """BME280 sensor using I2C interface"""
    
    def __init__(self, i2c, address=BME280_I2CADDR, **kwargs):
        self.i2c = i2c
        self.address = address
        super().__init__(**kwargs)
    
    def read(self, addr, n_bytes):
        """Read bytes from I2C"""
        return self.i2c.readfrom_mem(self.address, addr, n_bytes)
    
    def write(self, addr, byte):
        """Write byte to I2C"""
        self.i2c.writeto_mem(self.address, addr, bytes([byte]))


class BME280_SPI(BME280):
    """BME280 sensor using SPI interface"""
    
    def __init__(self, spi, cs, **kwargs):
        self.spi = spi
        self.cs = cs
        self.cs.init(self.cs.OUT, value=1)
        super().__init__(**kwargs)
    
    def read(self, addr, n_bytes):
        """Read bytes from SPI"""
        self.cs(0)
        self.spi.write(bytes([addr | 0x80]))
        data = self.spi.read(n_bytes)
        self.cs(1)
        return data
    
    def write(self, addr, byte):
        """Write byte to SPI"""
        self.cs(0)
        self.spi.write(bytes([addr & 0x7F, byte]))
        self.cs(1)
