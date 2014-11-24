'''
Created on Nov 13, 2014

This is the class that controls the TQ10X drivers.

@author: John Lorenz
'''

import serial
from time import sleep


BAUD_RATE = 9600

class CommCommunicator(object):
    
    def __init__(self, devices):
        self.devices = devices
        self.ser = None

    def open(self):
        '''Open the serial connection to the TQ10X driver'''
        print 'opening serial communication'
        for device in self.devices:
            try:
                self.ser = serial.Serial(device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.1)
                
                self.ser.write('#1\r')
                sleep(1)
                self.ser.write('1R\r')
		sleep(1)
                print 'writing "1R"'
                response = self.ser.read(10)
                print "read: "+str(response)+"\n"
                if "*" in str(response):
                    print 'response indicates TQ10X drivers, moving forward'
                    break
                else:
                    print 'response does not indicate TQ10x, next port'
                
            except Exception:
                print 'encountered exception'
                pass

        if self.ser is None:
            raise Exception
        
        sleep(2)
        
        commands = ["#1", "1OSA1", "2OSA1", "V1", "A1", "D0", "INE1"]
        self.sendCommands(commands)
        
    def close(self):
        self.ser.close()
        self.ser = None
    
    def sendCommands(self, commands):        
        for s in commands:
            self.ser.write(s+'\r')
            print self.ser.read(10)
        return True
    
    def moveArm(self, encoderCounts, direction, speed):
        commands = ["S", "A5", "V"+str(speed), "D"+str(encoderCounts), "G"]
        for i in range(len(commands)):
            commands[i] = str(direction)+commands[i];
        
        commandsSuccessful = self.sendCommands(commands);
        sleep(4);
        return commandsSuccessful;

if __name__ == '__main__':
    USB_devices = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2',
                   '/dev/ttyUSB3', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
    CC = CommCommunicator(USB_devices)
    CC.open()
    c = '1'
    while c!=0:
        c = raw_input('Command: ')
        s = c.split()
        CC.sendCommands(s)
        
        
