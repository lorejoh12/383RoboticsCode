'''
Created on Nov 13, 2014

Controls the serial communication with the ArduinoMega that controls the
hand on the arm. Rotates the wrist and opens and closes the grip.

@author: John Lorenz
'''

import serial
from time import sleep
from string import strip


BAUD_RATE = 9600

class UnoCommunicator(object):
    
    def __init__(self, devices):
        print 'devices: '+str(devices)
        self.devices = devices
        self.ser = None

    def open(self):
        '''Open the serial connection to the gripper arduino'''
        for device in self.devices:
            try:
                print device
                self.ser = serial.Serial(device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout= 1)

                self.ser.flushInput()
                self.ser.flushOutput()
                sleep(4)
                print 'writing: "A"'
                self.ser.write('A')
                sleep(2)
                response = self.ser.read(10)
                print 'Read back: '+str(response)
                if response=='2':
                    print 'response was ID=2, indicates Uno Arduino'
                    break
                
            except Exception, err:
                pass
        self.ser.write('B') #acknowldge ID received
        print "acknowledge ID receipt: "+ str(self.ser.read(10))
        sleep(2)
        
    def close(self):
        self.ser.close()
        self.ser = None
    
    def readFromUno(self):
        c = self.ser.read(20)
        return c
        
    def sendToUno(self, data):
        self.ser.write(data)
        response = self.ser.read(20)
        return response

if __name__ == '__main__':
    USB_devices = ['COM3', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
                   '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', 
                   '/dev/tty.PL2303-00001014', '/dev/tty.PL2303-00002014',
                   '/dev/tty.usbmodem1411', '/dev/tty.usbmodem1421']
    UC = UnoCommunicator(USB_devices)
    UC.open()
#     c = '1'
#     while c!=0:
#         c = raw_input('Command: ')
#         UC.sendData(c)
    while True:
        c = UC.readFromUno()
        if(c):
            print c