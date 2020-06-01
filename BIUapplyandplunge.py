#!/usr/bin/env python3

# Uncomment for use of pi
import RPi.GPIO as GPIO
#import Adafruit_DHT
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

def timeprocess(irsensor,exittime):
    tic = time.time()
    print(exittime)
    while GPIO.input(irsensor)==0 and time.time()-tic<exittime:
        pass
    toc=time.time()

    #print GPIO.input(pin.irsensor)
    total = toc - tic
    print("Time from start to immersion:", total)

def mixsample(cannon,mix,mixwait):
    GPIO.output(cannon,GPIO.HIGH)
    time.sleep(mix)
    print("mixing1")
    GPIO.output(cannon,GPIO.LOW)
    time.sleep(mixwait)
    
def applysample(cannon,spraywait,spray):
    #if mix != 0:
    #    print ('xxx')
    #if (mix or mixwait) != 0:
    #    GPIO.output(cannon,GPIO.HIGH)
    #    time.sleep(mix)
    #    #print("mixing")
    #    GPIO.output(cannon,GPIO.LOW)
    #    time.sleep(mixwait)
    #    #print("waiting")
    time.sleep(spraywait)
    GPIO.output(cannon,GPIO.HIGH)
    time.sleep(spray)
    GPIO.output(cannon,GPIO.LOW)
    
def releaseplunger(plunger,wait):
    time.sleep(wait)
    GPIO.output(plunger,GPIO.HIGH)

def resetplunger(plunger):
    GPIO.output(plunger,GPIO.LOW)
    
def readenvironment(dht22):
    humidity, temperature = Adafruit_DHT.read_retry(22, pin=dht22)
    return humidity, temperature
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Arguments for BIUcontrol')

    parser.add_argument('--mtime',      help='Duration of sample mixing (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--mdelay',     help='Time to wait after mixing (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--stime',      help='Duration of sample application (seconds)',type=float,required=True)
    parser.add_argument('--sdelay',     help='Time to wait before applying (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--pdelay',     help='Time to wait before plunging (seconds)',default = 0, type=float,required=False)
    parser.add_argument('--donotplunge',help='Do not fire the plunger (diagnostic)',action = 'store_true')  
    args = parser.parse_args()
    
    # Default timing
    cannontimetoreverse = 0.020
    cannonreversedelay  = args.stime + args.sdelay+ cannontimetoreverse
    timeout             = 1     # withdraw the plunger to avoid overheating
    kuhnketime          = 1

    GPIO.setwarnings(False)
      
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    GPIO.setup(pin.plunger,GPIO.OUT)
    GPIO.setup(pin.cannonposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.irsensor,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        
    # Report environmental conditions
#    humidity, temperature = readenvironment(pin.dht22)
#    print('Temp={0:0.1f}\'C  Humidity={1:0.1f}% RH'.format(temperature, humidity))

    # Display timing and avoid crash
    print("Timings:")
    print("Specimen application will start at time: ",args.sdelay)
    print("Specimen application will end at time: ",args.sdelay + args.stime)
    print("Cannon will reverse at time: ",cannonreversedelay)
    print("Plunger will fall at time: ",args.pdelay)
    exittime = kuhnketime+args.pdelay+args.sdelay
    print("Program will exit after: ",exittime)
    #if cannonreversedelay > args.pdelay:
    #    print("The cannon does not have sufficient time to reverse before plunging!!")
    #    exit()

    # Check interlock
    if GPIO.input(pin.interlock)==1:
        print("Interlock fail: cryogen container is not in place")
        powerdownsensors(pin.sensorpower)
        cannonreverse(pin.cannonposition,0)
        exit()
    else:
        print("Safety interlock pass: cryogen container is in place")

    # Mix sample if requested
    if args.mtime or args.mdelay !=0:
        print("mixing")
        mixsample(pin.cannon,args.mtime,args.mdelay)
        
    # set up parallel processes
    sample = threading.Thread(target=applysample, args=(pin.cannon,args.sdelay,args.stime))  
    plunger = threading.Thread(target=releaseplunger, args=(pin.plunger,args.pdelay))  
    cannonposition = threading.Thread(target=cannonreverse, args=(pin.cannonposition,cannonreversedelay))
    clockit = threading.Thread(target=timeprocess, args=(pin.irsensor,exittime))
    
    # start processes
    if not args.donotplunge:
        plunger.start()
        
    sample.start()  
    cannonposition.start()
    clockit.start()
    
    # Kuhnke plunger
    time.sleep(kuhnketime+args.pdelay+args.sdelay)
    resetplunger(pin.plunger)
    powerdownsensors(pin.sensorpower)

    GPIO.cleanup()
    print("Done!")

