"""
    mcu.py
    modified  : 2021-03-29
    desc.    : Runs micropython code on Raspberry Pi for sampling antenna, operates at various sampling speeds, and allows
               communication between a host computer (in this case a Raspberry Pi) to signal that samples were collected and
               allows transfer of data to host computer.
"""

from machine import UART, Pin, ADC, SPI
import utime
import time

# defines UART port
uart1 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))
# defines adc for sampling antenna
antenna_adc = machine.ADC(0)
# led
led_pin = Pin(25, Pin.OUT, Pin.PULL_UP)
samples_ready = False
# list to hold sample values
samples = []

def get_samples(adc, samples):
    for i in range(15000):
        samples.append(adc.read_u16())
    return samples

def _send_samples():
    global samples
    global samples_ready
    global uart1
    global led_pin
    
    if samples_ready:
        time.sleep(0.5)
        led_pin.value(0)
        val = ''
        for i in range(len(samples)):
            val = str(samples[i])
            val = str.encode(val)
            uart1.write(val)
        print("Sent {} values".format(len(samples)))
        samples_ready = False
        del samples
        led_pin.value(1)

def _sample_antenna():
    global samples_ready
    global antenna_adc
    global samples
    if not samples_ready:
        samples = []
        samples = get_samples(antenna_adc, samples)
        samples_ready = True
        print("SAMPLE READY")
    

def main():
    global samples_ready
    global samples
    global led_pin
    print("Initializing Pico Board for Antenna Sampling")
    # defines the antenna ADC port (pin 31)
    
    sensor_temp = machine.ADC(4)

    pwr = Pin(20, Pin.OUT, Pin.PULL_UP)
    led_pin.value(1)
    pwr.value(1)
    
    # signal_done is pico telling rpi it is done sampling
    signal_done = Pin(6, Pin.OUT)
    # signal_rdy is rpi telling pico it is ready to start sampling
    signal_rdy  = Pin(7, Pin.IN)
    signal_rdy.irq(lambda pin: _sample_antenna(), Pin.IRQ_FALLING)
    # receive_rdy is rpi telling pico to send samples
    receive_rdy = Pin(10, Pin.IN)
    receive_rdy.irq(lambda pin: _send_samples(), Pin.IRQ_FALLING)
    
    # defines states
    zero_rdy = 0
    pico_done = 0
    
    while(1):
        time.sleep(0.3)
        if samples_ready:
            signal_rdy.value(1)
            led_pin.toggle()
        else:
            signal_rdy.value(1)
main()
