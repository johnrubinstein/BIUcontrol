#!/usr/bin/env python3

from guizero import App, TextBox, Text, PushButton, CheckBox
from subprocess import call, Popen
import RPi.GPIO as GPIO
import BIUpinlist as pin

def startprocess():
    print("starting process")
    spraytime        = str(float(stime.value)/1000)
    retractiondelay  = str(float(rdelay.value)/1000)
    plungedelay      = str(float(pdelay.value)/1000)
    arguments = ["python3","BIUapplyandplunge.py","--stime",spraytime,"--rdelay",retractiondelay,"--pdelay",plungedelay]
    if donotplunge.value==1:
        arguments.append("--donotplunge")
    call(arguments)
    button_start.disable()
    
def powerup():
    print("Power up")
    arguments = ["python3","BIUpowerupdown.py","--updown","up"]
    call(arguments)
    button_start.enable()
    
def powerdown():
    print("Power down")
    arguments = ["python3","BIUpowerupdown.py","--updown","down"]
    call(arguments)
    button_start.disable()
    
def cleanprocess():
    print("starting clean process")
    spraytime  = str(float(cleantime.value)/1000)
    cycles = cleancycles.value
    arguments = ["python3","BIUclean.py","--stime",spraytime,"--cycles",cycles]
    #print(arguments)
    #call(arguments)
    Popen(arguments)
    #call(["python3","cleancontrol.py","--stime",stime,"--cycles",cycles])

def pedal():
    GPIO.setup(pin.pedalsensor,GPIO.IN, pull_up_down = GPIO.PUD_UP)
    if button_start.enabled and GPIO.input(pin.pedalsensor)==0:
        print("Pedal triggered")
        startprocess()

    
app = App(title="Back-it-up", layout="grid")
stimelabel  = Text(app, text="Spray time (msec)", grid=[0,1])
stime       = TextBox(app, grid=[1,1], text="30")
rdelaylabel = Text(app, text="Retraction delay (msec)", grid=[0,2])
rdelay      = TextBox(app, grid=[1,2], text="50")
pdelaylabel = Text(app, text="Plunge delay (msec)", grid=[0,3])
pdelay      = TextBox(app, grid=[1,3], text="50")




donotplunge = CheckBox(app, text="Do not plunge", grid=[0,4])
button_up   = PushButton(app, command=powerup,text="Ready", grid=[0,5])
button_down = PushButton(app, command=powerdown, text="Abort", grid=[1,5])
button_start= PushButton(app, command=startprocess, text="Spray & Plunge", grid=[0,6])
button_up.bg="orange"
button_start.bg = "red"
button_start.disable()

cleancycleslabel = Text(app, text="Cleaning cycles", grid=[3,1])
cleancycles      = TextBox(app, text="5",grid=[4,1])   
cleantimelabel   = Text(app, text="Cleaning pulse (msec)", grid=[3,2])
cleantime        = TextBox(app, text="200",grid=[4,2]) 
clean            = PushButton(app, command=cleanprocess, text="Clean", grid=[3,5])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
app.repeat(100,pedal)
app.display()


