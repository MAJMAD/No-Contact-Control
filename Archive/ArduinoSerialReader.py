import serial
import matplotlib.pyplot as plt
import numpy as np
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    #xpoint = 0
    #xpoints = []
    s1list = []
    s2list = []
    while True:
        #xpoint += 1
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            if line[:10] == "Sensor 1: ":
                s1list.append(float(line[10:]))
            if line[:10] == "Sensor 2: ":
                s1list.append(float(line[10:]))
            print(line)
#             if len(s1list) == len(s2list):
#                 plt.clf()
#                 plt.ion()
#                 plt.plot(xpoints,s1list, 'o')
#                 plt.plot(xpoints,s2list, 'o')
#                 plt.xlabel('Points')
#                 plt.ylabel('Sensor Readings')
#                 plt.show()
#     
#     plt.plot(xpoints,s1list, 'o')
#     plt.plot(xpoints,s2list, 'o')
#     plt.xlabel('Points')
#     plt.ylabel('Sensor Readings')
#     plt.savefig('sensor1.png')
#     plt.clf()
#     plt.plot(xpoints,avrdist2list, 'o')
#     plt.xlabel('Points')
#     plt.ylabel('Average distance of Sensor2')
#     plt.plot(xpoints,avrdist2list, 'o')
#     plt.savefig('sensor2.png')
#     print("Done")
#     f.close()
