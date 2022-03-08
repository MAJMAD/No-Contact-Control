from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from gpiozero import DistanceSensor
from threading import Thread

reading = True
sensor = DistanceSensor(echo=15, trigger=14)

def safe_exit(signum, frame):
    exit(1)
    
def read_distance():
    while reading:
        print("Distance: " + "{:1.2f}".format(sensor.value) + " m")
        sleep(0.1)
    
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

try:
    reader = Thread(target=read_distance, daemon=True)
    reader.start()
    
    pause()
    
except KeyboardInterrupt:
    pass

finally:
    reading = False
    sensor.close()