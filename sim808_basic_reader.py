import serial
import time
import io
import pynmea2


def to_decimal_degree(datum, direction):
    datum = float(datum)
    deg = int(datum/100.00)
    if direction in ["S", "W"]:
        return round (deg + (datum - (deg*100))/60.00, 6) * -1
    return round (deg + (datum - (deg*100))/60.00, 6)
    

def to_utc_time(time_string, UTC):

    hour = time_string.hour + UTC
    if hour < 0:
        hour +=24
     
    return str(time_string.hour + UTC).zfill(2) + ":" + str(time_string.minute).zfill(2) + ":" + str(time_string.second).zfill(2)
    
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

ser.write(str.encode('AT+CGNSPWR=1' + '\r\n'))
time.sleep(1)

ser.write(str.encode('AT+CGNSTST=1' + '\r\n'))
time.sleep(1)

UTC = -6 # UTC Time constant

while 1:
    try:
        line = sio.readline()
        msg = pynmea2.parse(line)
        if "$GPGGA" in line:
            print(to_decimal_degree(msg.lat, msg.lat_dir), to_decimal_degree(msg.lon, msg.lon_dir), msg.altitude, to_utc_time(msg.timestamp, UTC))
##            print(repr(msg))

    except serial.SerialException as e:
        print('Device error: {}'.format(e))
        break
    except pynmea2.ParseError as e:
##        print('Parse error: {}'.format(e))
        continue

ser.write(str.encode('AT+CGNSTST=0' + '\r\n'))
time.sleep(1)
ser.write(str.encode('AT+CGNSPWR=0' + '\r\n'))
time.sleep(1)

