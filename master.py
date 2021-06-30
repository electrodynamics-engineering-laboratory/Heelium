#!/usr/bin/env python3
import logging

#Imports from the Radio_Sender Lostik
import time
import sys
import serial
import argparse

#Imports from the BME280
import board
import busio
import adafruit_bme280

#Import from GPS
import gps
from serial.threaded import LineReader, ReaderThread

# ReaderThread
import heelium.py

# PrintLines Class
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
        txmsg = 'radio tx %x' % (int(time.time()))
        self.send_cmd(txmsg)
        time.sleep(2)
        txmsg1 = 'radio tx %x' % int(bme280.temperature*10)
        self.send_cmd(txmsg1)
        time.sleep(2)
        txmsg2 = 'radio tx %x' % abs(int(bme280.altitude*10))
        self.send_cmd(txmsg2)
        time.sleep(2)
        txmsg3 = 'radio tx %x' % abs(int(bme280.pressure*10))
        self.send_cmd(txmsg3)
        time.sleep(2)
        txmsg4 = 'radio tx %x' % abs(int(bme280.relative_humidity*10))
        self.send_cmd(txmsg4)
        time.sleep(2)
        #BME280 Code Stop
        report = session.next()
        txmsg5 = 'radio tx %x' % abs(int(report.alt*10))
        self.send_cmd(txmsg5)
        time.sleep(2)
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = self.frame_count + 1
    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s" % cmd)
        self.write_line(cmd)
        time.sleep(delay)

if __name__ == "__main__":
    # set up section for lostick
    parser = argparse.ArgumentParser(description='LoRa Radio mode sender.')
    parser.add_argument('port', help="Serial port descriptor")
    args = parser.parse_args()

    # set up section for bme280
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme280.sea_level_pressure = 1013.25

    # set up section for GPS
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    report = session.next()

    # main program loop
    ser = serial.Serial(args.port, baudrate=57600)
    with ReaderThread(ser, PrintLines) as protocol:
        while(1):
            protocol.tx()
            time.sleep(10)