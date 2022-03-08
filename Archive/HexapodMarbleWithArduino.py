from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from gpiozero import DistanceSensor, LED
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands
import serial

reading = True
#Usensor = DistanceSensor(echo=15, trigger=14)
#Vsensor = DistanceSensor(echo=5, trigger=0)
REFMODES = 'FRF'
AXES = ["X", "Y", "Z", "U", "V", "W"]
HOME = [0,0,0,0,0,0]
gUval = 0
gVval = 0
f = open('logfile.txt', 'w')
f.close()

# redPin1 = LED(22)
# greenPin1 = LED(27)
# bluePin1 = LED(17)
# redPin2 = LED(20)
# greenPin2 = LED(16) 
# bluePin2 = LED(21)
#     
# def redOn():
#     redPin1.on()
#     redPin2.on()
# 
# def redOff():
#     redPin1.off()
#     redPin2.off()
# 
# def greenOn():
#     greenPin1.on()
#     greenPin2.on()
# 
# def greenOff():
#     greenPin1.off()
#     greenPin2.off()
# 
# def blueOn():
#     bluePin1.on()
#     bluePin2.on()
# 
# def blueOff():
#     bluePin1.off()
#     bluePin2.off()
# 
# def yellowOn():
#     redPin1.on()
#     greenPin1.on()
#     redPin2.on()
#     greenPin2.on()
# 
# def yellowOff():
#     redPin1.off()
#     greenPin1.off()
#     redPin2.off()
#     greenPin2.off()

def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)

def safe_exit(signum, frame):
    exit(1)
    
def read_arduino():
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', 'ignore').rstrip()
            if len(line) > 15:
                line = line[:15]
            if line[:10] == "Sensor 1: ":
                gUval = float(line[10:])/50
            if line[:10] == "Sensor 2: ":
                gVval = float(line[10:])/50
        
def read_distance(pidevice, Umaxdist, Vmaxdist):
    f = open('logfile.txt','a')
    print("Done with initialization mode, entering operational mode", file = f)
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    #readArduino = Thread(target=read_arduino, args=())
    #readArduino.start()
    counter = 0
    lastUVal = 0
    lastVVal = 0
    Uval = 0
    Vval = 0
    retrigger = 0
    badmoves = 0
    readcount = 0
    pidevice.MOV(['U','V'], [0,0])
    #UArray = [0, 0, 0, 0, 0]
    #VArray = [0, 0, 0, 0, 0]
    f.close()
    while reading:
        f = open('logfile.txt','a')
        print("Readcount: " + str(readcount), file = f)
        print("Readcount: " + str(readcount))
        sleep(0.002)
        readcount += 1
        lock = 0
        badmoves = 0
        newreading = 1
        while newreading:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', 'ignore').rstrip()
                if len(line) > 15:
                    line = line[:15]
                if line[:10] == "stefan 1: ":
                    try:
                        Uval = float(line[10:])/80
                    except:
                        print("Error in reading Uval caught")
                        print("Error in reading Uval caught", file = f)
                        time.sleep(5)
                        Uval = lastUVal
                if line[:10] == "marcus 2: ":
                    try:
                        Vval = float(line[10:])/80
                    except:
                        print("Error in reading Vval caught")
                        print("Error in reading Vval caught", file = f)
                        time.sleep(5)
                        Vval = lastVVal
                if Uval != lastUVal or Vval != lastVVal:
                    newreading = 0
        print("U axis: " + str(Uval), file = f)
        print("V axis: " + str(Vval), file = f)
        print("U axis: " + str(Uval))
        print("V axis: " + str(Vval))
        #Uval = truncate(Uval,1)
        #Vval = truncate(Vval,1)
        Uval = round(Uval,1)
        Vval = round(Vval,1)
        print("U axis: " + str(Uval), file = f)
        print("V axis: " + str(Vval), file = f)
        print("U axis: " + str(Uval))
        print("V axis: " + str(Vval))
        if Uval > 0.9 or Uval < 0.1:
                #bluePin1.off()
                #greenPin1.off()
                #redPin1.on()
            lock += 1
        if Vval > 0.9 or Vval < 0.1:
                #bluePin2.off()
                #greenPin2.off()
                #redPin2.on()
            lock += 10
        if Uval < 0.075 and Vval < 0.075:
            pidevice.MOV(['U','V'],[14.95,0])
            sleep(1)
            pidevice.MOV(['U','V'],[0,0])
            sleep(1)
            ser.reset_input_buffer()
        if lock == 1:
            pidevice.MOV('V', Vmaxdist*(Vval-0.5))
        if lock == 10:
            pidevice.MOV('U', Umaxdist*(Uval-0.5))
        if lock == 0:
            pidevice.MOV(['U','V'], [Umaxdist*(Uval-0.5),Vmaxdist*(Vval-0.5)])
        if lastUVal == Uval and lastVVal == Vval:
            counter += 1
        elif retrigger == 1: 
            counter = 5000
        else: counter = 0
        lastUVal, lastVVal = Uval, Vval
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
                        Uval = float(line[10:])/100
                    if line[:10] == "marcus 2: ":
                        Vval = float(line[10:])/100
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
        f.close()
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
    #yellowOn()
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
    umin = -11.3
    umax = 11.3
    vmin = -11.3
    vmax = 11.3
    #yellowOff()
    pidevice.VLS(20)
    print("Done with initialization mode, entering operational mode")
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