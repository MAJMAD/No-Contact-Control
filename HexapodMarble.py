from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
#import RPi.GPIO as GPIO
from gpiozero import DistanceSensor, LED
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands

reading = True
Usensor = DistanceSensor(echo=15, trigger=14)
Vsensor = DistanceSensor(echo=5, trigger=0)
CONTROLLERNAME = 'C-887'
STAGES = None  # this controller does not need a 'stages' setting
REFMODES = 'FRF'
AXES = ["X", "Y", "Z", "U", "V", "W"]
HOME = [0,0,0,0,0,0]

redPin1 = LED(22)
greenPin1 = LED(27)
bluePin1 = LED(17)
redPin2 = LED(20)
greenPin2 = LED(16) 
bluePin2 = LED(21)

# def blink(pin):
#     GPIO.setmode(GPIO.BOARD)
#     
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.HIGH)
#     
# def turnOff(pin):
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.LOW)
    
def redOn():
    redPin1.on()
    redPin2.on()

def redOff():
    redPin1.off()
    redPin2.off()

def greenOn():
    greenPin1.on()
    greenPin2.on()

def greenOff():
    greenPin1.off()
    greenPin2.off()

def blueOn():
    bluePin1.on()
    bluePin2.on()

def blueOff():
    bluePin1.off()
    bluePin2.off()

def yellowOn():
    redPin1.on()
    greenPin1.on()
    redPin2.on()
    greenPin2.on()

def yellowOff():
    redPin1.off()
    greenPin1.off()
    redPin2.off()
    greenPin2.off()

def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)

def safe_exit(signum, frame):
    exit(1)
    
def read_distance(pidevice, Umaxdist, Vmaxdist):
    counter = 0
    lastUVal = 0
    lastVVal = 0
    retrigger = 0
    badmoves = 0
    UArray = [0, 0, 0, 0, 0]
    VArray = [0, 0, 0, 0, 0]
    while reading:
        #print(truncate(pidevice.qPOS('X')['X'], 4), truncate(pidevice.qPOS('Y')['Y'], 4), truncate(pidevice.qPOS('Z')['Z'], 4), truncate(pidevice.qPOS('U')['U'], 4), truncate(pidevice.qPOS('V')['V'], 4), truncate(pidevice.qPOS('W')['W'], 4))
        sleep(0.2)
        lock = 0
        for value in range(0,4):
            UArray[value] = UArray[value+1]
            VArray[value] = VArray[value+1]
            #print(value)
        UArray[4] = Usensor.value
        VArray[4] = Vsensor.value
        Uval = sum(UArray)/5
        Vval = sum(VArray)/5
        print("U axis: " + str(Uval))
        print("V axis: " + str(Vval))
        if Uval > 0.9 or Uval < 0.1:
            bluePin1.off()
            greenPin1.off()
            redPin1.on()
            lock += 1
        if Vval > 0.9 or Vval < 0.1:
            bluePin2.off()
            greenPin2.off()
            redPin2.on()
            lock += 10
#         print(pidevice.qVMO(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))))
        if pidevice.qVMO(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))) == False:
#             tar = pidevice.qTRA(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)))
#             tar['U'], tar['V'] = truncate(tar['U'], 2), truncate(tar['V'], 2)
            badmoves = 1
            
        if lock == 0 and badmoves == 0:
            redOff()
            blueOff()
            greenOn()
#             print("lock = 0 badmoves = 0")
#             print("U Distance: " + "{:1.2f}".format(Uval) + " m")
#             print("Moving U to: " + "{:1.2f}".format(Umaxdist*(Uval-0.5)))
#             print("V Distance: " + "{:1.2f}".format(Vval) + " m")
#             print("Moving V to: " + "{:1.2f}".format(Vmaxdist*(Vval-0.5)))
#             print(Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))
            pidevice.MOV(('U','V'), (Umaxdist*(Uval-0.5), Vmaxdist*(Vval-0.5)))#
            WaitForMotionDone(pidevice, 'U')
            WaitForMotionDone(pidevice, 'V')
#             print("Finished Good Moves")
            #sleep(0.2)
        if lock == 0 and badmoves == 1:
            redOff()
            blueOff()
            greenOn()
            tar = pidevice.qTRA(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)))
           # print(tar)
            tar['U'], tar['V'] = truncate(tar['U'], 1), truncate(tar['V'], 1)
           # print(tar)
           # print("lock = 0 badmoves = 1")
           # print("U Distance: " + "{:1.2f}".format(Uval) + " m")
           # print("Moving U to: " + "{:1.2f}".format(tar['U']))
           # print("V Distance: " + "{:1.2f}".format(Vval) + " m")
            #print("Moving V to: " + "{:1.2f}".format(tar['V']))
           # print(Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))
            pidevice.MOV(('U','V'), (tar['U'], tar['V']))
            WaitForMotionDone(pidevice, 'U')
            WaitForMotionDone(pidevice, 'V')
#             print("Finished Good Moves")
            #sleep(0.2)
        elif lock == 1:
            bluePin2.off()
            redPin2.off()
            greenPin2.on()
#             print("lock = 1 Deadzoning U")
            goodmove = pidevice.qVMO(('V',), (Vmaxdist*(Vval-0.5),))
            if goodmove == False:
                #print(pidevice.qPOS())
                tar = pidevice.qTRA(('V',), (Vmaxdist*(Vval-0.5),))
                #print(tar)
                tar['V'] = truncate(tar['V'], 1)
                #print(tar)
                #print("V Distance: " + "{:1.2f}".format(Vval) + " m")
                #print("Moving V to: " + "{:1.2f}".format(tar['V']))
                pidevice.MOV(('V'),(tar['V'])) ###############errored out
                WaitForMotionDone(pidevice, 'V')
            else:
#                 print("V Distance: " + "{:1.2f}".format(Vval) + " m")
                #print("Moving V to: " + "{:1.2f}".format(tar['V']))
                pidevice.MOV(('V',),(Vmaxdist*(Vval-0.5),))
                WaitForMotionDone(pidevice, 'V')
                
#             print("Finished Deadzone U Moves")
            #sleep(0.2)
        elif lock == 10:
            bluePin1.off()
            redPin1.off()
            greenPin1.on()
#             print("lock = 10 Deadzoning V")
            goodmove = pidevice.qVMO(('U',), (Umaxdist*(Uval-0.5),))
            if goodmove == False:
                tar = pidevice.qTRA(('U',), (Umaxdist*(Uval-0.5),))
                tar['U'] = truncate(tar['U'], 1)
#                 print(tar)
#                 print("U Distance: " + "{:1.2f}".format(Vval) + " m")
#                 print("Moving U to: " + "{:1.2f}".format(tar['U']))
                pidevice.MOV(('U',),(tar['U'],))
                WaitForMotionDone(pidevice, 'U')
            else:
#                 print("U Distance: " + "{:1.2f}".format(Uval) + " m")
#                 print("Moving U to: " + "{:1.2f}".format(tar['U']))
                pidevice.MOV(('U',),(Umaxdist*(Uval-0.5),))
                WaitForMotionDone(pidevice, 'U')
#             print("Finished Deadzone V Moves")
            #sleep(0.2)
        else:
            pass
             #print("Deadzone")
#             print("Billys Great")
#             print("Finished Deadzone")
            #sleep(0.2)
        if lastUVal == Uval and lastVVal == Vval:
            counter += 1
        elif retrigger == 1: 
            counter = 200
        else: counter = 0
#         print(counter)
        lastUVal, lastVVal = Uval, Vval
#         print(lastUVal, lastVVal )
        if counter >= 200:
            redOff()
            greenOff()
            blueOn()
            pidevice.MAC_START("MOTION")
            isRunning = True
            while isRunning:
                isRunning = pidevice.IsRunningMacro()
#                 print(isRunning)
                if isRunning == False: 
                    #isRunning = True
                    retrigger = 1
                Uval = Usensor.value
                Vval = Vsensor.value
#                 print(Uval,Vval)
                if Uval > 0.075 and Vval > 0.075:
                    pass
                else:
#                     print("debugging")
                    pidevice.STP(noraise=True)
                    blueOff()
                    redOn()
                    greenOn()
                    sleep(2.0)
                    pidevice.MOV(AXES,HOME)
                    WaitForMotionDone(pidevice, 'X')
                    WaitForMotionDone(pidevice, 'Y')
                    WaitForMotionDone(pidevice, 'Z')
                    WaitForMotionDone(pidevice, 'U')
                    WaitForMotionDone(pidevice, 'V')
                    WaitForMotionDone(pidevice, 'W')
                    pidevice.MOV(AXES,HOME)
                    WaitForMotionDone(pidevice, 'X')
                    WaitForMotionDone(pidevice, 'Y')
                    WaitForMotionDone(pidevice, 'Z')
                    WaitForMotionDone(pidevice, 'U')
                    WaitForMotionDone(pidevice, 'V')
                    WaitForMotionDone(pidevice, 'W')
                    pidevice.SPI(('R','S','T'),(0,0,0))
                    sleep(2.0)
                    isRunning = False
                    counter = 0
                    retrigger = 0
    
def WaitForMotionDone(device, axis):
    isMoving = True
    while isMoving:
        isMoving = device.IsMoving(axis)[axis]

def ConnectController():
    gateway = PISerial("/dev/ttyUSB0", 115200)
    #gateway = PISocket('172.31.0.147', 50000)
    messages = GCSMessages(gateway)
    gcs = GCSCommands(gcsmessage = messages)
    gcs.SVO(AXES[0],1)
    gcs.SVO(AXES[1],1)
    gcs.SVO(AXES[2],1)
    gcs.SVO(AXES[3],1)
    gcs.SVO(AXES[4],1)
    gcs.SVO(AXES[5],1)
    gcs.FRF(AXES)
    referencing = False
    while not referencing:
        referencing = gcs.IsControllerReady()
    return gateway, messages, gcs

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

def main():
    yellowOn()
    sleep(1)
    yellowOff()
    greenOn()
    sleep(1)
    greenOff()
    redOn()
    sleep(1)
    redOff()
    blueOn()
    sleep(1)
    gateway, messages, pidevice = ConnectController()
    print(pidevice.qIDN())
    #Transport Position Facilitation
    pidevice.MOV('X', 0)
    pidevice.MOV('Y', 0)
    pidevice.MOV('U', 0)
    pidevice.MOV('V', 0)
    pidevice.MOV('Z', -9.6)
    pidevice.MOV('W', 2.6)
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'U')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    sleep(1.0)
    #return to origin
    pidevice.MOV('X', 0)
    pidevice.MOV('Y', 0)
    pidevice.MOV('U', 0)
    pidevice.MOV('V', 0)
    pidevice.MOV('Z', 0)
    pidevice.MOV('W', 0)
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'U')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    umin = -18.75
    umax = 18.75
    vmin = -18.75
    vmax = 18.75
    yellowOff()
    try:
        reader = Thread(target=read_distance(pidevice, umax-umin, vmax-vmin), daemon=True)
        reader.start()
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        reading = False
        Usensor.close()
        Vsensor.close()
        gateway.close()
        
if __name__ == '__main__':
    main()
