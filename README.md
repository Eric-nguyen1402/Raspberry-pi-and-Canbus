# Raspberry-pi-and-Canbus
First you need to add can library :
* Python 3
- pip3 install python-can
* Python 2
- pip install python-can
# How to use Can in raspberry pi:
 1. sudo apt-get update
 2. sudo apt-get upgrade
 3. sudo apt-get install can-utils
 4. sudo reboot
 5. sudo nano /boot/config.txt
 - dtoverlay=mcp2515-can0,oscillator=10000000,interrupt=25 
 - dtoverlay=spi1-1cs
 7. sudo nano /etc/network/interfaces
 - auto can0
 - iface can0 can static
 - bitrate 125000
