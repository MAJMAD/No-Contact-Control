from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from gpiozero import DistanceSensor, LED
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands

reading = True
Usensor = DistanceSensor(echo=15, trigger=14)
Vsensor = DistanceSensor(echo=5, trigger=0)
REFMODES = 'FRF'
AXES = ["X", "Y", "Z", "U", "V", "W"]
HOME = [0,0,0,0,0,0]

redPin1 = LED(22)
greenPin1 = LED(27)
bluePin1 = LED(17)
redPin2 = LED(20)
greenPin2 = LED(16) 
bluePin2 = LED(21)
    
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
        sleep(0.2)
        lock = 0
        for value in range(0,4):
            UArray[value] = UArray[value+1]
            VArray[value] = VArray[value+1]
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
        if pidevice.qVMO(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))) == False:
            badmoves = 1
        if lock == 0 and badmoves == 0:
            redOff()
            blueOff()
            greenOn()
            pidevice.MOV(('U','V'), (Umaxdist*(Uval-0.5), Vmaxdist*(Vval-0.5)))#
            WaitForMotionDone(pidevice, 'U')
            WaitForMotionDone(pidevice, 'V')
        if lock == 0 and badmoves == 1:
            redOff()
            blueOff()
            greenOn()
            tar = pidevice.qTRA(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)))
            tar['U'], tar['V'] = truncate(tar['U'], 1), truncate(tar['V'], 1)
            pidevice.MOV(('U','V'), (tar['U'], tar['V']))
            WaitForMotionDone(pidevice, 'U')
            WaitForMotionDone(pidevice, 'V')
        elif lock == 1:
            bluePin2.off()
            redPin2.off()
            greenPin2.on()
            goodmove = pidevice.qVMO(('V',), (Vmaxdist*(Vval-0.5),))
            if goodmove == False:
                tar = pidevice.qTRA(('V',), (Vmaxdist*(Vval-0.5),))
                tar['V'] = truncate(tar['V'], 1)
                pidevice.MOV(('V'),(tar['V'])) ###############errored out
                WaitForMotionDone(pidevice, 'V')
            else:
                pidevice.MOV(('V',),(Vmaxdist*(Vval-0.5),))
                WaitForMotionDone(pidevice, 'V')
        elif lock == 10:
            bluePin1.off()
            redPin1.off()
            greenPin1.on()
            goodmove = pidevice.qVMO(('U',), (Umaxdist*(Uval-0.5),))
            if goodmove == False:
                tar = pidevice.qTRA(('U',), (Umaxdist*(Uval-0.5),))
                tar['U'] = truncate(tar['U'], 1)
                pidevice.MOV(('U',),(tar['U'],))
                WaitForMotionDone(pidevice, 'U')
            else:
                pidevice.MOV(('U',),(Umaxdist*(Uval-0.5),))
                WaitForMotionDone(pidevice, 'U')
        else:
            pass
        if lastUVal == Uval and lastVVal == Vval:
            counter += 1
        elif retrigger == 1: 
            counter = 200
        else: counter = 0
        lastUVal, lastVVal = Uval, Vval
        if counter >= 200:
            redOff()
            greenOff()
            blueOn()
            pidevice.MAC_START("MOTION")
            isRunning = True
            while isRunning:
                isRunning = pidevice.IsRunningMacro()
                if isRunning == False: 
                    retrigger = 1
                Uval = Usensor.value
                Vval = Vsensor.value
                if Uval > 0.075 and Vval > 0.075:
                    pass
                else:
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
    gateway, messages, pidevice = ConnectController()
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
