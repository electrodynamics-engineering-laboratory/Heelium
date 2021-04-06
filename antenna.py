"""
    antenna.py
    modified : 2021-03-29
    desc.    : Controls RPi Pico board and commands sampling starts, then receives incoming data
"""

import gpiozero
import logging
import serial
import shutil
import sys
import os
import time
from datetime import datetime

if __name__ == "__main__":
	# initializes logging for antenna runs
	FORMAT = '%(levelname)s: %(message)s'
	logPath= os.path.join('log', 'antenna.log')
	logging.basicConfig(filename=logPath, level=logging.DEBUG, filemode='w', format=FORMAT)
	logger = logging.getLogger(logPath)
	try:
		# initialize serial port on serial0
		serialPort = serial.Serial('/dev/ttyAMA0', 115200, timeout=10) # serialPort read timeout for 10 seconds
		serialPort.open()
		# opens data file for saving samples
		dataFile = open("data/antenna-data", 'a')
		dataFile.write("STARTING COLLECTION AT: {}".format(datetime.now()))
		logger.info("STARTING COLLECTION AT: {}".format(datetime.now()))
	except Exception as e:
		serialPort.close()
		logger.error(e)
		sys.exit(-1)
	try:
		# initialze GPIO for controlling pico
		startSample = gpiozero.OutputDevice(pin=13, active_high=False, initial_value=False)	# GPIO13 at pin 33
		sendData 	= gpiozero.OutputDevice(pin=19, active_high=False, initial_value=False)	# GPIO19 at pin 35
		checkReady  = gpiozero.InputDevice(pin=26, pull_up=False)	# GPIO26 at pin 37
	except Exception as e:
		logger.error(e)
		sys.exit(-2)
	startTime = time.time()	# program start time
	currentTime = time.time()
	i = 0
	while ( (currentTime - startTime) < 18000):		# runs while time is less than 5 hours (18000 seconds)
		# running counter of number of samples
		i += 1
		# tell Pi to start sampling by activating Pico sample IRQ
		startSample.on()
		startSample.off()
		logger.info("Sample {} Commanded at: {}".format(i, datetime.now()))
		# if samples ready, activate receive gpio
		while(checkReady.is_active == False):
			time.sleep(0.001)
		
		# command data output (half second delay in pico to send data)
		sendData.on()
		# read in 2 x 15k 8-bit values and  write to data file
		data = serialPort.read(size=30000)
		dataFile.write("DATA {}: {}\n".format(datetime.now(), data))
		sendData.off()
		logger.info("Data collection {} commanded and completed at: {}".format(i, datetime.now()))
		# check current time
		currentTime = time.time()