#!/usr/bin/env python3

# Uncomment for use of pi
import RPi.GPIO as GPIO
import time, threading
import argparse
import sys, select
import BIUpinlist as pin

def cannonforward(cannonposition):
    print("Advancing the cannon")
    GPIO.output(cannonposition,GPIO.HIGH)

def powerupsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.HIGH)

def powerdownsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.LOW)
    
def cannonreverse(cannonposition,cannonreversedelay):
    time.sleep(cannonreversedelay)
    print("reversing the cannon")
    GPIO.output(cannonposition,GPIO.LOW)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Arguments for SIOpowerupdown')
    parser.add_argument('--updown',      help='Power up or down',required=True)
    args = parser.parse_args()

    GPIO.setwarnings(False)
    GPIO.cleanup()    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannonposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.irsensor,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
    if args.updown == 'up':
        # Power up sensors and check interlock
        powerupsensors(pin.sensorpower)
        if GPIO.input(pin.interlock)==1:
            print("Interlock fail: cryogen container is not in place")
            powerdownsensors(pin.sensorpower)
            cannonreverse(pin.cannonposition,0)
            exit()
        else:
            print("Safety interlock pass: cryogen container is in place")
            # put cannon into place and wait
            cannonforward(pin.cannonposition)
    elif args.updown == 'down':
        powerdownsensors(pin.sensorpower)
        cannonreverse(pin.cannonposition,0)
    print("Done!")

