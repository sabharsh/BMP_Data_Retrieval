# BMP_Data_Retrieval

## Description

The purpose of this module is to retrieve and format data of a BMP280 sensor using a Pyboard. It was created to write data directly to a data logging file and thus the primary function returns a formatted string. The data sheet used to parse the datafeed is:

https://cdn-shop.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf

## Functions

`get_bmp_data(bus)` - This is the primary function which calls all other functions and returns a formatted string. The returned value is `"<temperature (in C)>, <pressure (in Pa)>"`. It uses the I2C (3) to read the data from the BMP sensor. Refer to pinout diagram below:

http://micropython.org/resources/pyblitev10ac-pinout.jpg

`get_reg_dig(bus)` - This function reads and returns the register data of the BMP sensor which is used for calibration. The returned value is `[<DIG_T1>,<DIG_T2>,<DIG_T3>,<DIG_P1>,<DIG_P2>,<DIG_P3>,<DIG_P4>,<DIG_P5>,<DIG_P6>]`.

`get_temperature_pressure(bus, calb)` - This function uses the register values to calibrate, read and compute the temperature and pressure values. The returned value is `[<temperature (in C)>, <pressure (in Pa)>]`.
