# Jacob Mader 12/22/2021
# Developed for the purpose of evaluating the precision of HC-sr04 distance sensors
from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from gpiozero import DistanceSensor, LED
from threading import Thread
from pipython.pidevice.interfaces.piserial import PISerial
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands
import sys

reading = True
Usensor = DistanceSensor(echo=15, trigger=14)
Vsensor = DistanceSensor(echo=5, trigger=0)

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

def safe_exit(signum, frame):
    exit(1)
    
def read_distance(maxdist):
    UArray = []
    VArray = []
    UVariance = []
    VVariance = []
    redOn()
    with open('PrecisionAnalysisResults.txt', 'w') as f:
        while reading:
            for value in range(0,1000):
                sleep(0.15)
                UArray.append(Usensor.value*maxdist)
                VArray.append(Vsensor.value*maxdist)
                print("U Sensor Value #{}: {}".format(value, Usensor.value),file = f)
                print("V Sensor Value #{}: {}".format(value, Vsensor.value),file = f)
            redOff()
            blueOn()
            UsensorAverage = sum(UArray)/1000
            VsensorAverage = sum(VArray)/1000
            for value in range(0,1000):
                UVariance.append(abs(UArray[value]-UsensorAverage))
                VVariance.append(abs(VArray[value]-VsensorAverage))
                print("U Sensor Variance #{}: {}".format(value, UVariance[value]),file = f)
                print("V Sensor Variance #{}: {}".format(value, VVariance[value]),file = f)
            UsensorAverageVariance = sum(UVariance)/1000
            VsensorAverageVariance = sum(VVariance)/1000
            print("U Sensor Average Variance: {}".format(UsensorAverageVariance),file = f)
            print("V Sensor Average Variance: {}".format(VsensorAverageVariance),file = f)
            UsensorAboveAverageVariances = 0
            VsensorAboveAverageVariances = 0
            for value in range(0,1000):
                if UVariance[value] > UsensorAverageVariance:
                    UsensorAboveAverageVariances += 1
                if VVariance[value] > VsensorAverageVariance:
                    VsensorAboveAverageVariances += 1
            print("U Sensor Above Average Variances: {}".format(UsensorAboveAverageVariances),file = f)
            print("V Sensor Above Average Variances: {}".format(VsensorAboveAverageVariances),file = f)
            break
                    
def main():
    try:
        reader = Thread(target=read_distance(1))
        reader.start()
        blueOff()
        greenOn()
        #pause()
    except KeyboardInterrupt:
        pass
    finally:
        reading = False
        Usensor.close()
        Vsensor.close()
        
if __name__ == '__main__':
    main()