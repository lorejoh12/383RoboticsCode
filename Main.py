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
import math
import thread
import threading
'''
Movement notations:
    1. for comm_communicator.moveArm(a, b, c):
        a. a is encoder counts, i.e. amount of movement
            i. for vertical movement, a negative value makes the arm go up, and a positive value makes it go down
            ii. for horizontal movement, a negative value moves the arm left, and a positive value moves the arm right (when facing the back of the pumps)
        b. b tells the arm which direction to go
            i. a value of "1" tells the arm to move vertically
            ii. a value of "2" tells the arm to move horizontally
        c. c tells the arm how fast to move
            i. c can be any value between 0 and 7, with 7 being the fastest speed
            ii.  different speeds make the encoder counts go different distances
            iii. as you increase the value of c, your encoder becomes less accurate
    2. The translation between encoder counts and physical distances is as follows (assuming a speed of "1"):
        a. when moving vertically, 5000 encoder counts will make the arm move ~3 inches
        b. when moving horizontally 5000 encoder counts will make the arm move ~5 inches
        c. this relationship is relatively constant across all multiplicatives of encoder counts
'''
'''
global counters
'''
xCount = 0
zCount = 0
'''
positions:
'''
xDrink1 = 0 #right at beginning
xDrink2 = 9000 # 7" ahead of 0
xDrink3 = 18000 # 14" ahead of 0, 7" ahead of xDrink2
xDrink4 = 27000 # 21" ahead of 0
xDrink5 = 35000 # 28" ahead of 0
xBlock = 30000

zPump = 28000 #21" above resting point
zBar = 35000 #30" above resting point

xHolder = 30000 #~35" ahead of 0
zHolder = 60000 #37" above resting point

'''
orderList
'''
ordersList = [] #need to figure out how to link this with app
sizeList = [] #size list associated with each order

def goX(x):
    global xCount
    while xCount != x: #until you arrive at the appropriate x position
        print "x:", x
        print "xCount:", xCount
        if math.fabs(x-xCount) > 16000:
            if x-xCount > 0:
                comm_communicator.moveArm(16000, 2, 1)
                xCount += 16000
            else:
                comm_communicator.moveArm(-16000, 2, 1)
                xCount -= 16000
        else:
            comm_communicator.moveArm(x-xCount, 2, 1) #move the arm the correct encoder difference
            xCount += (x-xCount)# this will be positive or negative based on your position which you keep track of while the robot is on
        print "current xCount:", xCount
        
def goZ(z):
    global zCount
    while zCount != -z: #repeat for z position
        if z == 0:
            if math.fabs(-zCount) > 16000:
                comm_communicator.moveArm(16000, 1, 1)
                zCount += 16000
            else:
                comm_communicator.moveArm(-zCount, 1 , 1)
                zCount = 0
        else:
            if math.fabs(zCount + z) > 16000:
                if (zCount - z) < 0:
                    comm_communicator.moveArm(-16000, 1, 1)
                    zCount  -= 16000
                else:
                    comm_communicator.moveArm(16000, 1, 1)
                    zCount += 16000
            else:
                comm_communicator.moveArm(-1*(zCount + z), 1, 1)
                zCount += (-1*(zCount + z))
        print "zCount:", zCount
        
def goTo(x, z):
    global xCount
    global zCount
    if z == 0 or (zCount - z) > 0: #if z is going to move down
        goX(x) #move in the x direction first
        goZ(z)
    else: #otherwise, move up first
        goZ(z)
        goX(x)

def newDrink(size): # a lot of sudoCode here - path to grab correct cup and turn toward pumps 
    gripper_communicator.sendData('O')#open before arriving at cup
    
    if int(size) <= 12 and int(size) > 0: #--> rotation code for different sleeves
        gripper_communicator.sendData('L')
        gripper_communicator.sendData('S')
    elif int(size) <= 24 and int(size) > 12:
        gripper_communicator.sendData('R') #rotate arm toward larger sleeve
        gripper_communicator.sendData('S')
        #need to change this to account for encoder on claw rotation
        
    goTo(xHolder, zHolder) #go to cup sleeve with open, rotated claw
    
    gripper_communicator.sendData('C') #close claw around cup
    goZ(zPump) #Go to level of pumps   
    goX(xBlock)#make sure you're able to rotate 
    
    #rotate right towards pumps
    gripper_communicator.sendData('L')
    gripper_communicator.sendData('S')

def endDrink(): #give finished drink to customer, bar opposite the pumps
    #rotate 180 - assuimng an R/S gripper combo moves ~90 degrees
    if xCount > xBlock: #make sure you can rotate (i.e. you're last liquid wasn't 5)
        goX(xBlock)
    gripper_communicator.sendData('R')
    gripper_communicator.sendData('S')
    gripper_communicator.sendData('R')
    gripper_communicator.sendData('S')
    goZ(zBar)
    sleep(10) # Give user 10 seconds to grab onto drink
    gripper_communicator.sendData('O') #release the cup
    gripper_communicator.sendData('L') #turn back to straight-forward
    gripper_communicator.sendData('S')


def drinkPos(type): #move to drink position, determine based liquid type - want to add code for pumps to work
    x = xDrink1
    if type == 1:
        x = xDrink1
    elif type == 2:
        x = xDrink2
    elif type == 3:
        x = xDrink3
    elif type == 4:
        x = xDrink4
    elif type == 5:
        x = xDrink5
    goTo(x, zPump)

def goHome(): #go back to zero zero, should do this before turning off
    goTo(0,0)

def makeDrink(orders): #based on order sequence from the app - going to modify to add sizes
    while len(orders) != 0:
        for order in orders: #list of lists
            newDrink(12) #replace with size parameter
            for type in order: #list of liquids going into drink
                drinkPos(type)
                #pump_communicator.dispense_ml(29.5*12/len(order), 200) #replace 12 with size parameter
            endDrink()
            orders.remove(order)
    goHome()
    
def raw_input_with_timeout(prompt, timeout=30.0):
    print prompt,    
    timer = threading.Timer(timeout, thread.interrupt_main)
    astring = ""
    try:
        timer.start()
        astring = raw_input(prompt)
    except KeyboardInterrupt:
        pass
    timer.cancel()
    return astring

def Test():
    print "running test"
    for i in range(1,5): #1-5
        print "getting drink:", i
        drinkPos(i) #test going to every position
        print "arrived at position:", i
        gripper_communicator.sendData('L')
        gripper_communicator.sendData('S')
        sleep(1)
        gripper_communicator.sendData('R')
        gripper_communicator.sendData('S')
    print xCount
    print "going home"
    goHome()
    print "home"

#pump_device = '/dev/ttyAMA0' # the GPIO serial port on the RPI
USB_devices = [ '/dev/tty.PL2303-00001014', '/dev/tty.PL2303-00002014','/dev/tty.usbmodem1411', '/dev/tty.usbmodem1421', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
               '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']

BAUD_RATE = 9600


if __name__ == '__main__':
    comm_communicator = CommCommunicator.CommCommunicator(USB_devices)
    comm_communicator.open()
    # pump_communicator = PumpCommunicator.RouterDriver(pump_device, False)
    #pump_communicator.open()
    gripper_communicator = GripperCommunicator.GripperCommunicator(USB_devices)
    gripper_communicator.open()
    """
    MAIN FUNCTION
    """
#     kill = ""
#     while len(kill) == 0:
#         makeDrink(ordersList)
#         kill = raw_input_with_timeout("No more drinks in queue, would you like to stop operation?", 30)
    
    """
    TEST SECTION
    """
    #Test()
    #pump_communicator.dispense_ml(6, 200)
    #goZ(10000)
    #drinkPos(5)
    #gripper_communicator.sendData('L')
    #gripper_communicator.sendData('S')
    comm_communicator.close()
    #pump_communicator.close()
    gripper_communicator.close()

