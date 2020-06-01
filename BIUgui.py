#!/usr/bin/env python3

from guizero import App, TextBox, Text, PushButton, CheckBox
from subprocess import call, Popen

def startprocess():
    print("starting process")
    spraytime = str(float(stime.value)/1000)
    plungedelay = str(float(pdelay.value)/1000)
    spraydelay  = str(float(sdelay.value)/1000)
    mixtime = str(float(mtime.value)/1000)
    mixdelay = str(float(mdelay.value)/1000)
    arguments = ["python3","BIUapplyandplunge.py","--stime",spraytime,"--pdelay",
                 plungedelay,"--sdelay",spraydelay,"--mtime",mixtime,"--mdelay",mixdelay]
    #if mix.value==1:
    #    mixtime = str(float(mtime.value)/1000)
    #    mixdelay = str(float(mdelay.value)/1000)
    #    arguments.extend(("--mtime",mixtime,"--mdelay",mixdelay))
    if donotplunge.value==1:
        arguments.append("--donotplunge")
    print(arguments)
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
    Popen(arguments)

app = App(title="Back-it-up", layout="grid")

# specimen mixing
mtimelabel  = Text(app, text="Mix time (msec)", grid=[0,0])
mtime       = TextBox(app, grid=[1,0], text="0")
mdelaylabel = Text(app, text="Mix delay (msec)", grid=[0,1])
mdelay      = TextBox(app, grid=[1,1], text="0")
# spray and plunge
stimelabel  = Text(app, text="Spray time (msec)", grid=[0,2])
stime       = TextBox(app, grid=[1,2], text="30")
pdelaylabel = Text(app, text="Plunge delay (msec)", grid=[0,3])
pdelay      = TextBox(app, grid=[1,3], text="45")
sdelaylabel = Text(app, text="Spray delay (msec)", grid=[0,4])
sdelay      = TextBox(app, grid=[1,4], text="0")
donotplunge = CheckBox(app, text="Do not plunge", grid=[0,5])
# cleaning
cleancycleslabel = Text(app, text="Cleaning cycles", grid=[3,3])
cleancycles      = TextBox(app, text="5",grid=[4,3])   
cleantimelabel   = Text(app, text="Cleaning pulse (msec)", grid=[3,4])
cleantime        = TextBox(app, text="200",grid=[4,4]) 
# buttons
button_up   = PushButton(app, command=powerup,text="Ready", grid=[0,6])
button_up.bg="orange"
button_down = PushButton(app, command=powerdown, text="Abort", grid=[1,6])
button_start= PushButton(app, command=startprocess, text="Spray & Plunge", grid=[0,7])
button_start.bg = "red"
clean            = PushButton(app, command=cleanprocess, text="Clean", grid=[3,6])
button_start.disable()

app.display()
