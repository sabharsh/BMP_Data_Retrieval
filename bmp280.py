"""    
    Primary Function: get_bmp_data() 
    Returned value: "<temperature>, <pressure>"
    
    Note: BMP280 sensor pins depend on the I2C bus created in the calling function.
    Reference: https://cdn-shop.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf
"""

from pyb import I2C
import struct
import time

BMP280_DEVICE_ADDRESS               = 0x77
BMP280_REGISTER_DIG_T1              = 0x88
BMP280_REGISTER_DIG_T2              = 0x8A
BMP280_REGISTER_DIG_T3              = 0x8C

BMP280_REGISTER_DIG_P1              = 0x8E
BMP280_REGISTER_DIG_P2              = 0x90
BMP280_REGISTER_DIG_P3              = 0x92
BMP280_REGISTER_DIG_P4              = 0x94
BMP280_REGISTER_DIG_P5              = 0x96
BMP280_REGISTER_DIG_P6              = 0x98
BMP280_REGISTER_DIG_P7              = 0x9A
BMP280_REGISTER_DIG_P8              = 0x9C
BMP280_REGISTER_DIG_P9              = 0x9E

BMP280_REGISTER_CHIPID             = 0xD0
BMP280_REGISTER_VERSION            = 0xD1
BMP280_REGISTER_SOFTRESET          = 0xE0

BMP280_REGISTER_CAL26              = 0xE1  # R calibration stored in 0xE1-0xF0

BMP280_REGISTER_CONTROL            = 0xF4
BMP280_REGISTER_CONFIG             = 0xF5
BMP280_REGISTER_PRESSUREDATA       = 0xF7
BMP280_REGISTER_TEMPDATA           = 0xFA

def get_bmp_data():
    """This function returns the temperature and pressure as a formatted string."""
    
    i2c = I2C(3, I2C.MASTER) # create and init as a master
    reg_content = get_reg_dig(i2c)
    temperature, pressure = get_temperature_pressure(i2c, reg_content)
    # print("\ntemperature: {} C\npressure: {} Pa\n".format(temperature, pressure))
    i2c.deinit()
    
    return "{}, {}".format(temperature, pressure)

def get_reg_dig(bus):
    """This function retrieves the register values which are used for calibration."""
    reg_content = bus.mem_read(24,BMP280_DEVICE_ADDRESS, BMP280_REGISTER_DIG_T1) # reads all the data in bulk
    reg_content = list(struct.unpack('<HhhHhhhhhhhh', bytes(reg_content))) #unpacking the bytes read to int values keeping datatype size in mind
    reg_content = [float(i) for i in reg_content]

    DIG_T1 = reg_content[0]
    DIG_T2 = reg_content[1]
    DIG_T3 = reg_content[2]
    DIG_P1 = reg_content[3]
    DIG_P2 = reg_content[4]
    DIG_P2 = reg_content[4]
    DIG_P3 = reg_content[5]
    DIG_P4 = reg_content[6]
    DIG_P5 = reg_content[7]
    DIG_P6 = reg_content[8]
    DIG_P7 = reg_content[9]
    DIG_P8 = reg_content[10]
    DIG_P9 = reg_content[11] 

    # print("calb1: " + str(DIG_T1))
    # print("calb2: " + str(DIG_T2))
    # print("calb3: " + str(DIG_T3))
    # print("calb4: " + str(DIG_P1))
    # print("calb5: " + str(DIG_P2))
    # print("calb6: " + str(DIG_P3))
    # print("calb7: " + str(DIG_P4))
    # print("calb8: " + str(DIG_P5))
    # print("calb9: " + str(DIG_P6))
    # print("calb10: " + str(DIG_P7))
    # print("calb11: " + str(DIG_P8))
    # print("calb12: " + str(DIG_P9))

    return reg_content

def get_temperature_pressure(bus, calb):
    """This function computes the temperature and pressure using the register values."""
    
    # COMPUTING TEMPERATURE
    bus.mem_write(BMP280_REGISTER_TEMPDATA, BMP280_DEVICE_ADDRESS, BMP280_REGISTER_CONTROL, timeout=1000)
    raw_temp_data = bytearray(3)
    raw_temp_data = bus.mem_read(3, BMP280_DEVICE_ADDRESS, BMP280_REGISTER_TEMPDATA) # reads 3 bytes of temperature data
    # print(raw_temp_data)
    temp_msb  = raw_temp_data[0]
    temp_lsb  = raw_temp_data[1]
    temp_xlsb = raw_temp_data[2]
    # print(temp_xlsb)
    temp_xlsb = temp_xlsb >> 4
    # print(temp_msb)
    # print(temp_lsb)
    # print(temp_xlsb)
    UT = (temp_msb << 12) + (temp_lsb << 4) + (temp_xlsb)
    # print(UT)

    var1 = (UT / 16384.0 - calb[0] / 1024.0) * calb[1]
    var2 = ((UT / 131072.0 - calb[0] / 8192.0) * (UT / 131072.0 - calb[0] / 8192.0)) * calb[2]
    fine_temp =  (var1 + var2)
    temperature = fine_temp/5120.0 # Final temperature value in Celsius
    
    # COMPUTING PRESSURE
    bus.mem_write(BMP280_REGISTER_PRESSUREDATA, BMP280_DEVICE_ADDRESS, BMP280_REGISTER_CONTROL, timeout=1000)
    raw_press_data = bytearray(3)
    raw_press_data = bus.mem_read(3, BMP280_DEVICE_ADDRESS, BMP280_REGISTER_PRESSUREDATA) # reads 3 bytes of pressure data
    # print(raw_press_data)
    press_msb  = raw_press_data[0]
    press_lsb  = raw_press_data[1]
    press_xlsb = raw_press_data[2]
    # print(press_xlsb)
    press_xlsb = press_xlsb >> 4
    # print(press_msb)
    # print(press_lsb)
    # print(press_xlsb)
    UP = (press_msb << 12) + (press_lsb << 4) + (press_xlsb)
    # print(UP)
    var1 = (fine_temp / 2.0) - 64000.0
    var2 = var1 * var1 * (calb[8] / 32768.0)
    var2 = var2 + var1 * (calb[7] * 2)
    var2 = (var2 / 4.0) + (calb[6] * 65536.0)
    var1 = (calb[5] * var1 * var1 / 524288.0 + calb[4] * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * calb[3]
    p    = 1048576.0 - UP
    p    = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = calb[11] * p * p / 2147483648.0
    var2 = p * calb[10] / 32768.0

    pressure = p + (var1 + var2 + calb[9]) / 16.0 # Final pressure value in Pascals
    return [temperature, pressure]
    
def get_temperature(bus, calb):
    """This function computes the temperature (only) using the register values."""
    bus.mem_write(BMP280_REGISTER_TEMPDATA,BMP280_DEVICE_ADDRESS,BMP280_REGISTER_CONTROL, timeout=1000)
    raw_temp_data = bytearray(3)
    raw_temp_data = bus.mem_read(3,BMP280_DEVICE_ADDRESS, BMP280_REGISTER_TEMPDATA) # reads all the data in bulk
    # print(raw_temp_data)
    temp_msb  = raw_temp_data[0]
    temp_lsb  = raw_temp_data[1]
    temp_xlsb = raw_temp_data[2]
    # print(temp_xlsb)
    temp_xlsb = temp_xlsb >> 4
    # print(temp_msb)
    # print(temp_lsb)
    # print(temp_xlsb)
    UT = (temp_msb << 12) + (temp_lsb << 4) + (temp_xlsb)
    # print(UT)

    var1 = (UT / 16384.0 - calb[0] / 1024.0) * calb[1]
    var2 = ((UT / 131072.0 - calb[0] / 8192.0) * (UT / 131072.0 - calb[0] / 8192.0)) * calb[2]
    return ((var1 + var2)/5120.0)