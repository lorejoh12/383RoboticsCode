'''
Created on Nov 13, 2014

This is the main class for controlling the ECE383 Bartender Robot.
It is porting the serial communication used in past projects over into
python

@author: John Lorenz
'''

from time import sleep
import CommCommunicator
import PumpCommunicator
import GripperCommunicator
#arm_device = 'COM1'
# pump_device = 'COM1'
pump_device = '/dev/ttyAMA0' # the GPIO serial port on the RPI
USB_devices = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
               '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']

BAUD_RATE = 9600


if __name__ == '__main__':
    comm_communicator = CommCommunicator.CommCommunicator(USB_devices)
    comm_communicator.open()
    pump_communicator = PumpCommunicator.RouterDriver(pump_device, False)
    pump_communicator.open()
    gripper_communicator = GripperCommunicator.GripperCommunicator(USB_devices)
    gripper_communicator.open()
    
    pump_communicator.dispense_ml(6, 200)
    comm_communicator.moveArm(-10000, 1, 1)
    gripper_communicator.sendData('R')
    sleep(2)
    gripper_communicator.sendData('S')


    comm_communicator.close()
    pump_communicator.close()
    gripper_communicator.close()
    
