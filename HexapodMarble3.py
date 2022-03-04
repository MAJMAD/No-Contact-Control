from signal import pause
from time import sleep
from gpiozero import LED
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands
import serial, time

#globals
reading = True
AXES = ["X", "Y", "Z", "U", "V", "W"]
HOME = [0,0,0,0,0,0]
HEXAPODRANGE = 8
HEXAPODVELOCITY = 50
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
    redOn()
    greenOn()

def yellowOff():
    redOff()
    greenOff()
        
def read_distance(pidevice, Umaxdist, Vmaxdist):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    counter = 0
    lastUVal = 0.5
    lastVVal = 0.5
    Uval = 0
    Vval = 0
    retrigger = 0
    pidevice.MOV(['U','V'], [0,0])
    while reading:
        readcount += 1
        lock = 0
        newreading = 1
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', 'ignore').rstrip()
            print(line)
            if len(line) > 15:
                line = line[:15]
            if line[:10] == "stefan 1: ":
                try:
                    Uval = float(line[10:])
                except:
                    Uval = lastUVal
            if line[:10] == "marcus 2: ":
                try:
                    Vval = float(line[10:])
                except:
                    Vval = lastVVal
        #LED Control
        redOff()
        blueOff()
        greenOn()
        #Motion Control
        if Uval < 0.075 and Vval < 0.075 and readcount > 100:
            pidevice.MOV(['U','V'],[14.95,0])
            sleep(1)
            pidevice.MOV(['U','V'],[0,0])
            sleep(1)
            Uval, Vval = lastUVal, lastVVal
            ser.reset_input_buffer()
        pidevice.MOV(['U','V'], [Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)])
        #Macro Setup
        if lastUVal == Uval and lastVVal == Vval:
            counter += 1
        elif retrigger == 1: 
            counter = 5000
        else: counter = 0
        #Next loop setup
        lastUVal, lastVVal = Uval, Vval
        #Macro Functionality
        if counter >= 5000:
            pidevice.MAC_START("MOTION")
            isRunning = True
            while isRunning:
                isRunning = pidevice.IsRunningMacro()
                if isRunning == False: 
                    retrigger = 1
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    if line[:10] == "stefan 1: ":
                        Uval = float(line[10:])
                    if line[:10] == "marcus 2: ":
                        Vval = float(line[10:])
                if Uval > 0.075 and Vval > 0.075:
                    pass
                else:
                    pidevice.STP(noraise=True)
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
    gcs.SVO(AXES, [1,1,1,1,1,1])
    gcs.FRF(AXES)
    referencing = False
    while not referencing:
        referencing = gcs.IsControllerReady()
    return gateway, messages, gcs

def main():
    yellowOn()
    gateway, messages, pidevice = ConnectController()
    #Transport Position Facilitation
    pidevice.MOV(['X','Y','Z','U','V','W'], [0,0,-9.6,0,0,2.6])
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'U')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    sleep(1.0)
    #return to origin
    pidevice.MOV(AXES, HOME)
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'U')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    #lean to reveal maze orientation
    pidevice.MOV('U', 14)
    WaitForMotionDone(pidevice, 'U')
    sleep(10.0)
    #return to origin
    pidevice.MOV(AXES, HOME)
    WaitForMotionDone(pidevice, 'X')
    WaitForMotionDone(pidevice, 'Y')
    WaitForMotionDone(pidevice, 'U')
    WaitForMotionDone(pidevice, 'V')
    WaitForMotionDone(pidevice, 'Z')
    WaitForMotionDone(pidevice, 'W')
    umin, umax, vmin, vmax = -HEXAPODRANGE, HEXAPODRANGE, -HEXAPODRANGE, HEXAPODRANGE
    yellowOff()
    pidevice.VLS(HEXAPODVELOCITY)
    try:
        reader = Thread(target=read_distance(pidevice, umax-umin, vmax-vmin), daemon=True)
        reader.start()
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        reading = False
        gateway.close()
        
if __name__ == '__main__':
    main()