#Program asks for user input to determine color to shine.

import time, sys
import RPi.GPIO as GPIO

redPin1 = 15   #Set to appropriate GPIO
greenPin1 = 13 #Should be set in the 
bluePin1 = 11  #GPIO.BOARD format

redPin2 = 36  #Set to appropriate GPIO
greenPin2 = 38 #Should be set in the 
bluePin2 = 40  #GPIO.BOARD format

def blink(pin):
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    
def turnOff(pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    
def redOn():
    blink(redPin1)
    blink(redPin2)

def redOff():
    turnOff(redPin1)
    turnOff(redPin2)

def greenOn():
    blink(greenPin1)
    blink(greenPin2)

def greenOff():
    turnOff(greenPin1)
    turnOff(greenPin2)

def blueOn():
    blink(bluePin1)
    blink(bluePin2)

def blueOff():
    turnOff(bluePin1)
    turnOff(bluePin2)

def yellowOn():
    blink(redPin1)
    blink(greenPin1)
    blink(redPin2)
    blink(greenPin2)

def yellowOff():
    turnOff(redPin1)
    turnOff(greenPin1)
    turnOff(redPin2)
    turnOff(greenPin2)

def cyanOn():
    blink(greenPin)
    blink(bluePin)

def cyanOff():
    turnOff(greenPin)
    turnOff(bluePin)

def magentaOn():
    blink(redPin)
    blink(bluePin)

def magentaOff():
    turnOff(redPin)
    turnOff(bluePin)

def whiteOn():
    blink(redPin)
    blink(greenPin)
    blink(bluePin)

def whiteOff():
    turnOff(redPin)
    turnOff(greenPin)
    turnOff(bluePin)
    
print("""Ensure the following GPIO connections: R-11, G-13, B-15
Colors: Red, Green, Blue, Yellow, Cyan, Magenta, and White
Use the format: color on/color off""")

def main():
    while True:
        cmd = input("-->")


        if cmd == "red on":
            redOn()
        elif cmd == "red off":
            redOff()
        elif cmd == "green on":
            greenOn()
        elif cmd == "green off":
            greenOff()
        elif cmd == "blue on":
            blueOn()
        elif cmd == "blue off":
            blueOff()
        elif cmd == "yellow on":
            yellowOn()
        elif cmd == "yellow off":
            yellowOff()
        elif cmd == "cyan on":
            cyanOn()
        elif cmd == "cyan off":
            cyanOff()
        elif cmd == "magenta on":
            magentaOn()
        elif cmd == "magenta off":
            magentaOff()
        elif cmd == "white on":
            whiteOn()
        elif cmd == "white off":
            whiteOff()
        else:
            print("Not a valid command")
        
        
    return
    

main()
    
