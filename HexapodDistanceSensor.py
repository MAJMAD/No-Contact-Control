from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from gpiozero import DistanceSensor
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands

reading = True
#sensor = DistanceSensor(echo=5, trigger=0)
sensor = DistanceSensor(echo=15, trigger=14)
CONTROLLERNAME = 'C-887'
STAGES = None  # this controller does not need a 'stages' setting
REFMODES = 'FRF'
AXES = ["X", "Y", "Z", "U", "V", "W"]

def safe_exit(signum, frame):
    exit(1)
    
def read_distance(pidevice, maxdist):
    while reading:
        print("Distance: " + "{:1.2f}".format(sensor.value) + " m")
        print("Moving to: " + "{:1.2f}".format(maxdist*(sensor.value-0.5)))
        pidevice.MOV('U', maxdist*(sensor.value-0.5))
        WaitForMotionDone(pidevice, 'U')
        sleep(0.2)
    
def WaitForMotionDone(device, axis):
    isMoving = True
    while isMoving:
        isMoving = device.IsMoving(axis)[axis]

def ConnectController():
    gateway = PISerial("/dev/ttyUSB0", 115200)
    messages = GCSMessages(gateway)
    gcs = GCSCommands(gcsmessage = messages)
    return gateway, messages, gcs

def main():
    gateway, messages, pidevice = ConnectController()
    print(pidevice.qIDN())
    #Find travel range
    zmin = pidevice.qTMN('U')
    zmax = pidevice.qTMX('U')
    print(int(zmin['U']), int(zmax['U']))
    #Move to Start Position (Z-Min)
    pidevice.MOV('U', zmin['U'])
    WaitForMotionDone(pidevice, 'U')
    try:
        reader = Thread(target=read_distance(pidevice, zmax['U']-zmin['U']), daemon=True)
        reader.start()
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        reading = False
        sensor.close()
        gateway.close()
        
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)
        
    
if __name__ == '__main__':
    main()