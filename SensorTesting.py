import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
import numpy as np


loopcounter = 1
missedtriggers = 0
avrdistance1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
avrdistance2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
avrdist1list = []
avrdist2list = []
xpoints = []
sensor1misreads = 0
sensor2misreads = 0
_timeStart = 0

def startTimer():
    _timerStart = (time.time() * 1000)
    return _timerStart
    
def isTimerReady(mSec, _timerStart):
    return ((time.time()*1000 - _timerStart) < mSec)

settletime = 500
sensitivity = 5
f = open('logfile_' + str(settletime) + '_' + str(sensitivity) + '.txt', 'w')
f.close()
PIN_TRIGGER1 = 14
PIN_TRIGGER2 = 0
PIN_ECHO1 = 15
PIN_ECHO2 = 5
pulse1_start_time = 0
pulse1_end_time  =  0
pulse2_start_time = 0
pulse2_end_time  =  0
trigs = (PIN_TRIGGER1,PIN_TRIGGER2)
echos = (PIN_ECHO1,PIN_ECHO2)

while loopcounter < 1000:
      f = open('logfile_' + str(settletime) + '_' + str(sensitivity) + '.txt','a')
      GPIO.setmode(GPIO.BCM)

      GPIO.setup(trigs, GPIO.OUT)
      GPIO.setup(echos, GPIO.IN)

      GPIO.output(trigs, GPIO.LOW)

      print("Waiting for sensor to settle", file = f)
      _timerStart = startTimer()

      while not(isTimerReady(settletime, _timerStart)):
          pass

      print("Calculating distance", file = f)

      GPIO.output(trigs, GPIO.HIGH)

      time.sleep(0.00001)

      GPIO.output(trigs, GPIO.LOW)
      
      echo_start_time = time.time()

      while GPIO.input(PIN_ECHO1)== 0 or GPIO.input(PIN_ECHO2)== 0 :
            pulse1start= time.time()
            pulse2start=pulse1start
            if GPIO.input(PIN_ECHO1)== 0:
                pulse1_start_time = pulse1start
            if GPIO.input(PIN_ECHO2)== 0:
                pulse2_start_time = pulse2start
            if time.time() - echo_start_time > 0.5:
                print("Trigger missed, resending trigger", file = f)
                missedtriggers+=1
                GPIO.output(trigs, GPIO.HIGH)
                time.sleep(0.00001)
                GPIO.output(trigs, GPIO.LOW)
                echo_start_time = time.time()
            #print("Echos low")
      while GPIO.input(PIN_ECHO1)== 1 or GPIO.input(PIN_ECHO2)== 1:
            pulse1end, pulse2end = time.time(), time.time()
            if GPIO.input(PIN_ECHO1)== 1:
              pulse1_end_time = pulse1end
            if GPIO.input(PIN_ECHO2)== 1:
                pulse2_end_time = pulse2end
            #print("Echos high")

      pulse1_duration = pulse1_end_time - pulse1_start_time
      pulse2_duration = pulse2_end_time - pulse2_start_time
      distance1 = round(pulse1_duration * 17150, )
      distance2 = round(pulse2_duration * 17150, )
      
#       print("Sensor 1 Start Time:", pulse1_start_time,"sec")
#       print("Sensor 2 Start Time:", pulse2_start_time,"sec")
#       print("Sensor 1 End Time:", pulse1_end_time,"sec")
#       print("Sensor 2 End Time:", pulse2_end_time,"sec")
      print("Cycle:",loopcounter, file = f)
      print("Cycle:",loopcounter)
      print("Distance 1:",distance1,"cm", file = f)
      print("Distance 2:",distance2,"cm", file = f)
      
      if distance1 > 10000 or distance1 < -10000:
          distance1 = 90
      if distance2 > 10000 or distance2 < -10000:
          distance2 = 90
      
      avrdistance1[0:19], avrdistance1[19] = avrdistance1[1:20], distance1
      avr1 = sum(avrdistance1[0:20])/20
      avrdistance2[0:19], avrdistance2[19] = avrdistance2[1:20], distance2
      avr2 = sum(avrdistance2[0:20])/20
      
      print("Average Distance 1:",avr1,"cm","Averaged data",avrdistance1,file = f)
      print("Average Distance 2:",avr2,"cm","Averaged data",avrdistance2,file = f)
      
      
      
      if loopcounter > 8:
          if avr1 - 90 > sensitivity or avr1 - 90 < -1*sensitivity:
              sensor1misreads+=1
          if avr2 - 90 > sensitivity or avr2 - 90 < -1*sensitivity:
              sensor2misreads+=1
          avrdist1list.append(avr1)
          avrdist2list.append(avr2)
          xpoints.append(loopcounter)
      
      GPIO.cleanup()
      
      loopcounter+=1
      f.close()
f = open('logfile_' + str(settletime) + '_' + str(sensitivity) + '.txt','a')
print("Cycles: 1000", file = f)
print("Missed Triggers:",missedtriggers, file = f)
print("Sensor 1 Misreads:",sensor1misreads, file = f)
print("Sensor 2 Misreads:",sensor2misreads, file = f)
#xpoints = np.array([0,1001])
plt.plot(xpoints,avrdist1list, 'o')
plt.xlabel('Points')
plt.ylabel('Average distance of Sensor1')
plt.savefig('sensor1.png')
plt.clf()
plt.plot(xpoints,avrdist2list, 'o')
plt.xlabel('Points')
plt.ylabel('Average distance of Sensor2')
plt.plot(xpoints,avrdist2list, 'o')
plt.savefig('sensor2.png')
print("Done")
f.close()
