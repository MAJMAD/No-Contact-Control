from inputs import get_gamepad
import math
import threading
import time
from pipython.pidevice.interfaces.pisocket import PISocket
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.gcscommands import GCSCommands
# import logging
#logging.basicConfig(level=logging.DEBUG)

CONTROLLERNAME = 'C-887'
STAGES = None  # this controller does not need a 'stages' setting
REFMODES = 'FRF'
AXES = ["X", "Y", "Z", "U", "V", "W"]
STEPSIZE = 0.1

def WaitForMotionDone(device, axis):
    isMoving = True
    while isMoving:
        isMoving = device.IsMoving(axis)[axis]

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self): # return the buttons/triggers that you care about in this methode
        time.sleep(0.003)
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        z = self.RightJoystickY
        south = self.A
        east = self.B
        west = self.X
        north = self.Y
        rb = self.RightBumper
        lb = self.LeftBumper
        lt = self.LeftTrigger
        rt = self.RightTrigger
        return [x, y, z, south, east, west, north,lb, rb, lt, rt]

    def debounce(self, event, state): #debounces button events
        x = self.read()[event]
        if state != x:
            #time.sleep(0.025)
            x = self.read()[event]
        return x


    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_WEST':
                    self.X = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state




if __name__ == '__main__':
    joy = XboxController()
    gateway = PISocket('169.254.7.154', 50000)
    messages = GCSMessages(gateway)
    pidevice = GCSCommands(gcsmessage = messages)
    lastaxis = AXES[0]
    keyaxis = lastaxis
    for axis in AXES:
        pidevice.MOV(axis, 0)
        rangemi = pidevice.qTMN()
        rangema = pidevice.qTMX()
        curpo = pidevice.qPOS()
        rangemin = rangemi[axis]
        rangemax = rangema[axis]
        curpos = curpo[axis]
        if curpos >= rangemax-0.1*rangemax:
            pidevice.MOV(axis,rangemax-0.1*rangemax)
            curpo = pidevice.qPOS()
            curpos = curpo[axis]
        if curpos <= rangemin+0.1*rangemin:
            pidevice.MOV(axis, rangemin + 0.1 * rangemin)
            curpo = pidevice.qPOS()
            curpos = curpo[axis]
    while True:
        time.sleep(0.01)
        wk = joy.read()
        for axis in AXES:
            curpo = pidevice.qPOS()
            curpos = curpo[axis]
            rangemi = pidevice.qTMN()
            rangema = pidevice.qTMX()
            rangemin = rangemi[axis]
            rangemax = rangema[axis]
            if curpos >= rangemax-0.25*rangemax:
                pidevice.MOV(axis,rangemax-0.25*rangemax)
                curpo = pidevice.qPOS()
                curpos = curpo[axis]
            if curpos <= rangemin-0.25*rangemin:
                pidevice.MOV(axis, rangemin - 0.25*rangemin)
                curpo = pidevice.qPOS()
                curpos = curpo[axis]


        # Left Joystick X Axis Up
        if wk[0] > 0.5: # Left Joystick X Axis Up
            print("Option 2 selected: Move U Negative")
            pidevice.MVR("U", -1)
            lastaxis = 'U'
            keyaxis = lastaxis
        # Left Joystick X Axis Down
        if wk[0] < -0.5:
            print("Option 3 selected: Move U Positive")
            pidevice.MVR("U", 1)
            lastaxis = 'U'
            keyaxis = lastaxis

        # Left Joystick Y Axis Up
        if wk[1] > 0.5:
            print("Option 4 selected: Move V Positive")
            pidevice.MVR("V", 1)
            lastaxis = 'V'
            keyaxis = lastaxis

        # Left Joystick Y Axis Up
        if wk[1] < -0.5:
            print("Option 5 selected: Move V Negative")
            pidevice.MVR("V", -1)
            lastaxis = 'V'
            keyaxis = lastaxis



        # Right Joystick
        if wk[2] > 0.5:
            print("Option 6 selected: Move Z Positive")
            pidevice.MVR("Z", 1)
            lastaxis = 'Z'
            keyaxis = lastaxis

        if wk[2] < -0.5:
            print("Option 7 selected: Move Z Negative")
            pidevice.MVR("Z", -1)
            lastaxis = 'Z'
            keyaxis = lastaxis

            # West + NBorth Button
        if wk[3] == 1:
            print("Option 8 selected: Transport Position")
            pidevice.MOV('X', 0)
            pidevice.MOV('Y', 0)
            pidevice.MOV('U', 0)
            pidevice.MOV('V', 0)
            pidevice.MOV('Z', -11)
            pidevice.MOV('W', 2.5)

        if wk[5] == 1 and wk[6] == 1:
            #x = joy.debounce(3, 1)
            #if x == 1:
                print("Option 14 selected: SPA")
                print(pidevice.qSPA())


        if wk[4] == 1:
            #x = joy.debounce(4, 1)
            #if x == 1:
                print("Option 9 selected: HLP")
                print(pidevice.qHLP())

        #West Button
        if wk[5] == 1:
            #x = joy.debounce(5, 1)
            #if x == 1:
                print("Option 10 selected: HOME")
                for axis in AXES:
                    pidevice.MOV(axis, 0)

        #North Button
        if wk[6] == 1:
            #x = joy.debounce(6, 1)
            #if x == 1:
                print("Option 11 selected: TRA?")
                print(pidevice.qTRA(keyaxis, 1))

        #Left Bumper Action
        if wk[7] == 1:
            #x = joy.debounce(7, 1)
            #if x == 1:
                print("Option 12 selected: HOME KEY AXIS")
                pidevice.MOV(keyaxis, 0)

        #Right Bumper Action
        if wk[8] == 1:
            #x = joy.debounce(8, 1)
            #if x == 1:
                print("Option 13 selected: CHANGE KEY AXIS")
                if keyaxis == AXES[0]:
                    keyaxis = AXES[1]
                elif keyaxis == AXES[1]:
                    keyaxis = AXES[2]
                elif keyaxis == AXES[2]:
                    keyaxis = AXES[0]

        # Left + Right Bumper Action
        if wk[8] == 1 and wk[7] == 1:
            #x = joy.debounce(7, 1)
            #y = joy.debounce(8, 1)
            #if x == 1 and y == 1:
                print("Option 0 selected: Escape")
                break

        #West+North Buttons
        if wk[5] == 1 and wk[6] == 1:
            #x = joy.debounce(3, 1)
            #if x == 1:
                print("Option 14 selected: SPA")
                print(pidevice.qSPA())

        #Left trigger
        if wk[9] > 0.05:
            pass
            #do something VMO? maybe

        #Right trigger
        if wk[10] > 0.05:
            print("Option 15 selected: Query Key Axis")
            print(keyaxis)