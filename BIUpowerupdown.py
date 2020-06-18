#!/usr/bin/env python3

# Uncomment for use of pi
import RPi.GPIO as GPIO
import time, threading
import argparse
import sys, select
import BIUpinlist as pin

def filterforward(filterposition):
    print("Advancing the filter")
    GPIO.output(filterposition,GPIO.HIGH)

def powerupsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.HIGH)

def powerdownsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.LOW)
    
def filterreverse(filterposition,filterreversedelay):
    time.sleep(filterreversedelay)
    print("reversing the filter")
    GPIO.output(filterposition,GPIO.LOW)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Arguments for SIOpowerupdown')
    parser.add_argument('--updown',      help='Power up or down',required=True)
    args = parser.parse_args()

    GPIO.setwarnings(False)
    GPIO.cleanup()    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.filterposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.pedalsensor,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
    if args.updown == 'up':
        # Power up sensors and check interlock
        powerupsensors(pin.sensorpower)
        if GPIO.input(pin.interlock)==1:
            print("Interlock fail: cryogen container is not in place")
            powerdownsensors(pin.sensorpower)
            filterreverse(pin.filterposition,0)
            exit()
        else:
            print("Safety interlock pass: cryogen container is in place")
            # put filter into place and wait
            filterforward(pin.filterposition)
    elif args.updown == 'down':
        powerdownsensors(pin.sensorpower)
        filterreverse(pin.filterposition,0)
    print("Done!")

