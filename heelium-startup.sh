#!/bin/bash
sudo lsusb
sudo apt-get install gpsd gpsd-clients
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo systemctl enable gpsd.socket
sudo systemctl start gpsd.socket
pip3 install gps