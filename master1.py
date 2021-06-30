#!/usr/bin/env python3
#Imports from the Radio_Sender Lostik
import time
import sys
import serial
import argparse

#Imports from the BME280
#import time
import board
import busio
import adafruit_bme280

#Import from GPS
import gps

from serial.threaded import LineReader, ReaderThread

import logging

import csv

class PrintLines(LineReader):

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd("sys set pindig GPIO11 0")
        self.send_cmd('sys get ver')
        self.send_cmd('radio get mod')
        self.send_cmd('radio get freq')
        self.send_cmd('radio get sf')
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 10')
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = 0

    def handle_line(self, data):
        if data == "ok":
            return
        print("RECV: %s" % data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def tx(self):
    	

        self.send_cmd("sys set pindig GPIO11 1")
        
        #BME280 Code Start
        #Time
        txmsg = 'radio tx %x' % (int(time.time()))
        self.send_cmd(txmsg)
        time.sleep(2)
        f = open("heeliumData1.txt", "a")
        f.write("Time- " + '%x' % int(time.time()) + "\n")
        f.close()
        
        #Temperature
        txmsg1 = 'radio tx %x' % int(bme280.temperature*10)
        self.send_cmd(txmsg1)
        time.sleep(2)
        f = open("heeliumData1.txt", "a")
        f.write("Temp- " + '%x' % int(bme280.temperature*10) + "\n")
        f.close()
        
        #BME280 Altitude
        txmsg2 = 'radio tx %x' % abs(int(bme280.altitude*10))
        self.send_cmd(txmsg2)
        time.sleep(2)
        f = open("heeliumData1.txt", "a")
        f.write("Alt1- " + '%x' % abs(int(bme280.altitude*10)) + "\n")
        f.close()
        
        #Pressure
        txmsg3 = 'radio tx %x' % abs(int(bme280.pressure*10))
        self.send_cmd(txmsg3)
        time.sleep(2)
        f = open("heeliumData1.txt", "a")
        f.write("Pres- " + '%x' % abs(int(bme280.pressure*10)) + "\n")
        f.close()
        
        #Humidity
        txmsg4 = 'radio tx %x' % abs(int(bme280.relative_humidity*10))
        self.send_cmd(txmsg4)
        time.sleep(2)
        f = open("heeliumData1.txt", "a")
        f.write("Hum- " + '%x' % abs(int(bme280.relative_humidity*10)) + "\n")
        f.close()
        #BME280 Code Stop
        
        report = session.next()
        if report['class'] == 'TPV':
        	lat = getattr(nx, 'lat', "Unknown")
			lon = getattr(nx, 'lon', "Unknown")
			print(lat, lon)
            if hasattr(report, 'alt'):
                txmsg5 = 'radio tx %x' % abs(int(report.alt*10))
                self.send_cmd(txmsg5)
                time.sleep(2)
                f = open("heeliumData1.txt", "a")
                f.write("Alt2- " + '%x' % int(report.alt*10) + "\n")
                f.close()
        
        
        
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = self.frame_count + 1

    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s" % cmd)
        self.write_line(cmd)
        time.sleep(delay)

"""
function to get positional data from GPS
"""
def getPositionData(gps):
	nx = gpsd.next()
	if nx['class'] == 'TPV':
		lat = getattr(nx, 'lat', "Unknown")
		lon = getattr(nx, 'lon', "Unknown")
	return lat, lon

if __name__ == "__main__":
    FORMAT = "%(asctime)s %(relativeCreated)d %(levelname)s %(message)s"
    logging.basicConfig(filename="heelium.log", format=FORMAT)
    logger = logging.getLogger()
    Lostik_Port = "/dev/ttyUSB0"
    GPS_Port = "/dev/ttyUSB1"
    try:
        #Lostik Setup
        parser = argparse.ArgumentParser(description='LoRa Radio mode sender.')
        parser.add_argument('port', help="Serial port descriptor")
        args = parser.parse_args()
    except Exception as e:
    	print("Error with Lostik setup")
        logger.error(e)
    try:
        #BME280 Setup
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        bme280.sea_level_pressure = 1013.25
    except Exception as e:
    	print("Error with BME280 setup")
        logger.error(e)

    try:
        #GPS Setup
        session = gps.gps("localhost", "2947")
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        ser = serial.Serial(args.port, baudrate=57600)
    except Exception as e:
    	print("Error with GPS setup")
        logger.error(e)
    
    try:
		with open('heelium-data-readable.csv', 'a', newline='') as f:
			    writer = csv.writer(f)
			    header = ["Frame", "Time", "Latitude", "Longitude", "Altitude 1", "Altitude 2", "Temperature", "Pressure", "Humidity"]
			    writer.writerows(header)
	except Exception as e:
		logger.error(e)

    try:
        with ReaderThread(ser, PrintLines) as protocol:
            while(1):
                try: 
                    protocol.tx()
                except Exception as e:
                    logger.error(e)
                time.sleep(10)
    except Exception as e:
        logger.error(e)






