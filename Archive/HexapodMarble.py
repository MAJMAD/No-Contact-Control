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
        sleep(0.17)
        lock = 0
        badmoves = 0
        for value in range(0,4):
            UArray[value] = UArray[value+1]
            VArray[value] = VArray[value+1]
        UArray[4] = Usensor.value
        VArray[4] = Vsensor.value
        #handling deadzone reading
        if UArray[4] == 1:
            UArray = [1,1,1,1,1]
        if VArray[4] == 1:
            VArray = [1,1,1,1,1]
        #hanlding reading after deadzone
        if UArray[4] != 1 and (UArray == [1,1,1,1,Usensor.value] or UArray == [0,0,0,0,Usensor.value]):
            UArray[0], UArray[1], UArray[2], UArray[3] = UArray[4],UArray[4],UArray[4],UArray[4]
        if VArray[4] != 1 and (VArray == [1,1,1,1,Vsensor.value] or VArray == [0,0,0,0,Vsensor.value]):
            VArray[0], VArray[1], VArray[2], VArray[3] = VArray[4],VArray[4],VArray[4],VArray[4]
        #handling lower deadzone transitions
        if UArray[4] > 0.1 and UArray[3] < 0.1:
            UArray[0], UArray[1], UArray[2], UArray[3] = UArray[4],UArray[4],UArray[4],UArray[4]
        if VArray[4] > 0.1 and VArray[3] < 0.1:
            VArray[0], VArray[1], VArray[2], VArray[3] = VArray[4],VArray[4],VArray[4],VArray[4]
        if UArray[4] < 0.1 and UArray[3] > 0.1:
            UArray[0], UArray[1], UArray[2], UArray[3] = UArray[4],UArray[4],UArray[4],UArray[4]
        if VArray[4] < 0.1 and VArray[3] > 0.1:
            VArray[0], VArray[1], VArray[2], VArray[3] = VArray[4],VArray[4],VArray[4],VArray[4]
        #handling upper deadzone transitions
        if UArray[4] > 0.9 and UArray[3] < 0.9:
            UArray[0], UArray[1], UArray[2], UArray[3] = UArray[4],UArray[4],UArray[4],UArray[4]
        if VArray[4] > 0.9 and VArray[3] < 0.9:
            VArray[0], VArray[1], VArray[2], VArray[3] = VArray[4],VArray[4],VArray[4],VArray[4]
        if UArray[4] < 0.9 and UArray[3] > 0.9:
            UArray[0], UArray[1], UArray[2], UArray[3] = UArray[4],UArray[4],UArray[4],UArray[4]
        if VArray[4] < 0.9 and VArray[3] > 0.9:
            VArray[0], VArray[1], VArray[2], VArray[3] = VArray[4],VArray[4],VArray[4],VArray[4]
        Uval = sum(UArray)/5
        Vval = sum(VArray)/5
#         print(UArray)
#         print(VArray)
#         print("U axis: " + str(Uval))
#         print("V axis: " + str(Vval))
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
        if Uval < 0.075 and Vval < 0.075:
            pidevice.MOV(['U','V'],[14.95,0])
        if lock == 0:
            bluePin1.off()
            greenPin1.on()
            redPin1.off()
            bluePin2.off()
            greenPin2.on()
            redPin2.off()
            if pidevice.qVMO(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5))) == False:
                badmoves = 100;
        if lock == 1:
            if pidevice.qVMO(('U', 'V'), (pidevice.qPOS('U')['U'],Vmaxdist*(Vval-0.5))) == False:
                badmoves = 1
            else: badmoves = -1
        if lock == 10:
            #print(pidevice.qPOS('V'))
            if pidevice.qVMO(('U', 'V'), (Umaxdist*(Uval-0.5),pidevice.qPOS('V')['V'])) == False:
                badmoves = 10
            else: badmoves = -10
        if lock == 0 and badmoves == 0:
            bluePin2.off()
            greenPin2.on()
            redPin2.off()
            bluePin1.off()
            greenPin1.on()
            redPin1.off()
            pidevice.MOV(('U','V'), (Umaxdist*(Uval-0.5), Vmaxdist*(Vval-0.5)))#
            #WaitForMotionDone(pidevice, 'U')
            #WaitForMotionDone(pidevice, 'V')
        if lock == 0 and badmoves == 100:
            bluePin2.off()
            greenPin2.on()
            redPin2.off()
            bluePin1.off()
            greenPin1.on()
            redPin1.off()
            tar = pidevice.qTRA(('U', 'V'), (Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)))
            tar['U'], tar['V'] = truncate(tar['U'], 1), truncate(tar['V'], 1)
            pidevice.MOV(('U','V'), (tar['U'], tar['V']))
            #WaitForMotionDone(pidevice, 'U')
            #WaitForMotionDone(pidevice, 'V')
        if lock == 1 and badmoves == -1:
            bluePin2.off()
            greenPin2.on()
            redPin2.off()
            pidevice.MOV(('V'),(Vmaxdist*(Vval-0.5)))
            #WaitForMotionDone(pidevice, 'V')
        if lock == 1 and badmoves == 1:
            bluePin2.off()
            greenPin2.on()
            redPin2.off()
            tar = pidevice.qTRA(('V'), (Vmaxdist*(Vval-0.5)))
            tar['V'] = truncate(tar['V'], 1)
            pidevice.MOV(('V'),(tar['V'])) 
            #WaitForMotionDone(pidevice, 'V')
        if lock == 10 and badmoves == -10:
            bluePin1.off()
            greenPin1.on()
            redPin1.off()
            pidevice.MOV(('U',),(Umaxdist*(Uval-0.5),))
            #WaitForMotionDone(pidevice, 'U')
        if lock == 10 and badmoves == 10:
            bluePin1.off()
            greenPin1.on()
            redPin1.off()
            tar = pidevice.qTRA(('U'), (Umaxdist*(Uval-0.5)))
            tar['U'] = truncate(tar['U'], 1)
            pidevice.MOV(('U'),(tar['U']))
            #WaitForMotionDone(pidevice, 'U')
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
                    yellowOn()
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
    #lean to reveal maze orientation
    pidevice.MOV('X', 0)
    pidevice.MOV('Y', 0)
    pidevice.MOV('V', 0)
    pidevice.MOV('Z', 0)
    pidevice.MOV('W', 0)
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    pidevice.MOV('U', 14)
    WaitForMotionDone(pidevice, 'U')
    sleep(10.0)
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
    umin = -12
    umax = 12
    vmin = -12
    vmax = 12
    yellowOff()
    pidevice.VLS(10)
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
