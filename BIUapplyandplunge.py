#!/usr/bin/env python3

# Uncomment for use of pi
import RPi.GPIO as GPIO
#import Adafruit_DHT
import time, threading
import argparse
import sys, select
import BIUpinlist as pin

def filterforward(filterposition):
    print("Advancing the cannon")
    GPIO.output(filterposition,GPIO.HIGH)

def powerupsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.HIGH)

def powerdownsensors(sensorpower):
    GPIO.output(sensorpower,GPIO.LOW)
    
def filterreverse(filterposition,filterreversedelay):
    time.sleep(filterreversedelay)
    print("reversing the filter")
    GPIO.output(filterposition,GPIO.LOW)

def applysample(cannon,duration):
    GPIO.output(cannon,GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(cannon,GPIO.LOW)
    
def releaseplunger(plunger,wait):
    time.sleep(wait)
    print("releasing the plunger")
    GPIO.output(plunger,GPIO.HIGH)

def resetplunger(plunger):
    GPIO.output(plunger,GPIO.LOW)
    
def readenvironment(dht22):
    humidity, temperature = Adafruit_DHT.read_retry(22, pin=dht22)
    return humidity, temperature
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Arguments for BIUcontrol')
    parser.add_argument('--stime',      help='Duration of sample application (seconds)',type=float,required=True)
    parser.add_argument('--rdelay',     help='Time to wait before retracting filter (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--pdelay',     help='Time to wait before plunging (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--donotplunge',help='Do not fire the plunger (diagnostic)',action = 'store_true')  
    args = parser.parse_args()
    
    # Default timing
    #cannontimetoreverse = 0.020
    #cannonreversedelay  = args.stime + args.sdelay+ cannontimetoreverse


    GPIO.setwarnings(False)
      
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    GPIO.setup(pin.plunger,GPIO.OUT)
    GPIO.setup(pin.filterposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    #GPIO.setup(pin.pedalsensor,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        
    # Report environmental conditions
#    humidity, temperature = readenvironment(pin.dht22)
#    print('Temp={0:0.1f}\'C  Humidity={1:0.1f}% RH'.format(temperature, humidity))

    # Display timing and avoid crash
    print("Timings:")
    print("Specimen application will start at time: 0")
    print("Specimen application will end at time: ",args.stime)
    print("Filter will retract at time: ",args.rdelay)
    print("Plunger will fall at time: ",args.pdelay)
    kuhnketime = 1 # time for which plunger is energized to plunge
    energizedtime = kuhnketime+max(args.pdelay,args.stime,args.rdelay)
    print("Plunger will remain energized until: ",energizedtime)
    print("Program will exit after: ",1+energizedtime)
    #if cannonreversedelay > args.pdelay:
    #    print("The cannon does not have sufficient time to reverse before plunging!!")
    #    exit()

    # Check interlock
    if GPIO.input(pin.interlock)==1:
        print("Interlock fail: cryogen container is not in place")
        powerdownsensors(pin.sensorpower)
        filterreverse(pin.filterposition,0)
        exit()
    else:
        print("Safety interlock pass: cryogen container is in place")

    # set up processes
    sample = threading.Thread(target=applysample, args=(pin.cannon,args.stime))
    filterposition = threading.Thread(target=filterreverse, args=(pin.filterposition,args.rdelay))
    plunger = threading.Thread(target=releaseplunger, args=(pin.plunger,args.pdelay))  

    
    # start processes
    if not args.donotplunge:
        plunger.start()
        
    sample.start()  
    filterposition.start()
    
    # Kuhnke plunger
    time.sleep(kuhnketime+args.pdelay)
    resetplunger(pin.plunger)
    if max(args.stime,args.pdelay,args.rdelay) != args.pdelay:
        sleep(1+max(args.stime,args.rdelay)-args.pdelay)
    powerdownsensors(pin.sensorpower)

    GPIO.cleanup()
    print("Done!")

