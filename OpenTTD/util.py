

import sys
import openttd.util as util


#---------------------------------
# type conversion
#---------------------------------
def int_to_bytes(int_value: int, byte_count:int, separator: bytes = b'\x00') -> bytearray:
	tmp_data = int_value.to_bytes(byte_count, sys.byteorder) + separator
	return tmp_data


def str_to_bytes(str_value:str, separator: bytes = b'\x00') -> bytearray:
	tmp_data = bytearray(str_value, "UTF-8") + separator
	return tmp_data


def bytes_to_int(byte_value: bytearray, signed=False) -> int:
	return int.from_bytes(byte_value, sys.byteorder, signed=signed)


def bytes_to_str(byte_value: bytearray) -> str:
	return byte_value.decode()


def bytes_to_bool(byte_value: bytearray) -> bool:
	return bool.from_bytes(byte_value, byteorder=sys.byteorder)

#---------------------------------
# type parse
#---------------------------------
def get_int_from_bytes(byte_value: bytearray, int_size: int, *, signed=False):
	int_value = bytes_to_int( byte_value[: int_size], signed=signed )
	return int_value, int_size


def get_bool_from_bytes(byte_value: bytearray, bool_size: int = 1):
	bool_value = bytes_to_bool( byte_value[: bool_size] )
	return bool_value, bool_size


def get_str_from_bytes(byte_value: bytearray) -> bool:
	str_value = bytes_to_str( byte_value[: byte_value.index(b'\x00')] )
	return str_value, len(str_value) + 1



DAYS_IN_YEAR = 365
LEAP_DAYS_IN_100_YEARS = 24
LEAP_DAYS_IN_400_YEARS = 97
DAYS_IN_100_YEARS = DAYS_IN_YEAR * 100 + LEAP_DAYS_IN_100_YEARS
DAYS_IN_400_YEARS = DAYS_IN_YEAR * 400 + LEAP_DAYS_IN_400_YEARS

DAYS_IN_4_YEARS = DAYS_IN_YEAR * 4 + 1
DAYS_TO_LEAP_YEAR = DAYS_IN_YEAR * 3 + 31 + 28


def ConvertYMDToDate(year, month, day):

	is_leap_yr = False

	if (year % 4 == 0 and year % 100 != 0) or (year % 100 == 0 and year % 400 == 0):
		is_leap_yr = True

	num_400_yrs = int(year / 400)
	year = year % 400

	num_100_yrs = int(year / 100)
	year = year % 100

	num_4_yr = int(year / 4)
	year = (year % 4)

	date = year * DAYS_IN_YEAR + num_4_yr * DAYS_IN_4_YEARS + num_100_yrs * DAYS_IN_100_YEARS + num_400_yrs * DAYS_IN_400_YEARS

	for i in range(0, month - 1):
		date += list(util.MONTH_DAYS.values())[i]

		if is_leap_yr and i == 1:
			date += 1

	return date + day



def ConvertDateToYMD(date):
	num_400_yrs = int(date / DAYS_IN_400_YEARS)
	date = date - (num_400_yrs *  DAYS_IN_400_YEARS)

	num_100_yrs = int(date / DAYS_IN_100_YEARS)
	date = date - (num_100_yrs *  DAYS_IN_100_YEARS)

	num_4_yrs = int(date / DAYS_IN_4_YEARS)
	date = date - (num_4_yrs * DAYS_IN_4_YEARS)

	num_yrs = int(date / DAYS_IN_YEAR)
	date = date - (num_yrs * DAYS_IN_YEAR)

	year = num_100_yrs * 100 + num_400_yrs * 400 + num_4_yrs * 4 + num_yrs

	if date == 0:
		return year, 12, 31
	
	is_leap = False
	if date > DAYS_TO_LEAP_YEAR:
		is_leap = True

	month = 0

	while date > 0:
		month += 1
		date -= list(util.MONTH_DAYS.values())[ month - 1]

		if is_leap and month == 2:
			date -= 1
	
	date = list(util.MONTH_DAYS.values())[ month - 1] + date

	return year, month, date
