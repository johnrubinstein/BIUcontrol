#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, argparse
import BIUpinlist as pin

if __name__=='__main__':

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    
    parser = argparse.ArgumentParser(description='Arguments for cleanprocess')
    parser.add_argument('--stime', help='Duration of cleaning pulse (seconds)', default = 0.2, type=float,required=False)
    parser.add_argument('--cycles', help='number of cleaning pulses',default = 5, type=int,required=False)
    args = parser.parse_args()

    for x in range(args.cycles):
        GPIO.output(pin.cannon,GPIO.HIGH)
        time.sleep(args.stime)
        GPIO.output(pin.cannon,GPIO.LOW)
        time.sleep(0.2)
    
GPIO.cleanup()
