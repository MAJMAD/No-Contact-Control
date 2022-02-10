import RPi.GPIO as GPIO
import time

loopcounter = 1
missedtriggers = 0
lastdistance1 = 0
lastdistance2 = 0
sensor1misreads = 0
sensor2misreads = 0
while loopcounter < 1000:
      GPIO.setmode(GPIO.BCM)

      PIN_TRIGGER1 = 7
      PIN_TRIGGER2 = 8
      PIN_ECHO1 = 11
      PIN_ECHO2 = 9
      pulse1_start_time = 0
      pulse1_end_time  =  0
      pulse2_start_time = 0
      pulse2_end_time  =  0
      
      trigs = (PIN_TRIGGER1,PIN_TRIGGER2)
      echos = (PIN_ECHO1,PIN_ECHO2)

      GPIO.setup(trigs, GPIO.OUT)
      GPIO.setup(echos, GPIO.IN)

      GPIO.output(trigs, GPIO.LOW)

      print("Waiting for sensor to settle")

      time.sleep(1)

      print("Calculating distance")

      GPIO.output(trigs, GPIO.HIGH)

      time.sleep(0.00001)

      GPIO.output(trigs, GPIO.LOW)
      
      echo_start_time = time.time()

      while GPIO.input(PIN_ECHO1)== 0 or GPIO.input(PIN_ECHO2)== 0 :
            (pulse1_start_time, pulse2_start_time) = (time.time(), time.time())
            if time.time() - echo_start_time > 0.50:
                print("Trigger missed, resending trigger")
                missedtriggers+=1
                GPIO.output(trigs, GPIO.HIGH)
                time.sleep(0.00001)
                GPIO.output(trigs, GPIO.LOW)
                echo_start_time = time.time()
            #print("Echos low")
      while GPIO.input(PIN_ECHO1)== 1 or GPIO.input(PIN_ECHO2)== 1:
            (pulse1_end_time, pulse2_end_time) = (time.time(), time.time())
            #print("Echos high")

      pulse1_duration = pulse1_end_time - pulse1_start_time
      pulse2_duration = pulse2_end_time - pulse2_start_time
      distance1 = round(pulse1_duration * 17150, 2)
      distance2 = round(pulse2_duration * 17150, 2)
      
#       print("Sensor 1 Start Time:", pulse1_start_time,"sec")
#       print("Sensor 2 Start Time:", pulse2_start_time,"sec")
#       print("Sensor 1 End Time:", pulse1_end_time,"sec")
#       print("Sensor 2 End Time:", pulse2_end_time,"sec")
      print("Cycle:",loopcounter)
      print("Distance 1:",distance1,"cm")
      print("Distance 2:",distance2,"cm")
      
      if distance1 - lastdistance1 > 0.08*lastdistance1 or distance1 - lastdistance1 < -0.08*lastdistance1:
          sensor1misreads+=1
          
      if distance2 - lastdistance2 > 0.08*lastdistance2 or distance2 - lastdistance2 < -0.08*lastdistance2:
          sensor2misreads+=1
      
      lastdistance1, lastdistance2 = distance1,distance2
      
      GPIO.cleanup()
      
      loopcounter+=1
print("Cycles: 1000")
print("Missed Triggers:",missedtriggers)
print("Sensor 1 Misreads:",sensor1misreads)
print("Sensor 2 Misreads:",sensor2misreads)