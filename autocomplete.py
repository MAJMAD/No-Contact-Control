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
    while 1:
        #setup
        sleep(5)
        pidevice.MOV(['U','V'], [0,Vmaxdist])
        sleep(22)
        #throughfirstgate
        pidevice.MOV('V',-Vmaxdist)
        sleep(0.75)
        #setup
        pidevice.MOV(['U','V'], [-Umaxdist,0])
        sleep(19)
        #throughsecondgate
        pidevice.MOV('U',Umaxdist)
        sleep(1)
        #setup
        pidevice.MOV(['U','V'], [0,-Vmaxdist])
        sleep(19)
        #throughthirdgate
        pidevice.MOV('V',Vmaxdist)
        sleep(0.8)
        #setup
        pidevice.MOV('U', -Umaxdist)
        sleep(5)
        pidevice.MOV('U', 0)
        sleep(8)
        #throughlastgate
        pidevice.MOV('V', -Vmaxdist)
        sleep(1)
        #ramp
        pidevice.MOV(['U','V'],[Umaxdist,0])
        sleep(3)
    
    
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
        reader = Thread(target=read_distance(pidevice, umax, vmax), daemon=True)
        reader.start()
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        reading = False
        gateway.close()
        
if __name__ == '__main__':
    main()