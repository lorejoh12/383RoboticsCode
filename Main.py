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
        a. "a" is encoder counts, i.e. amount of movement
            i.  For vertical movement, a negative value makes the arm go up, and a positive value makes it go down
            ii. For horizontal movement, a negative value moves the arm left, and a positive value moves the arm right 
                (when facing the back of the pumps)
        b. "b" tells the arm which direction to go
            i.  A value of "1" tells the arm to move vertically
            ii. A value of "2" tells the arm to move horizontally
        c. "c" tells the arm how fast to move
            i.   "c" can be any value between 0 and 7, with 7 being the fastest speed
            ii.  different speeds make the encoder counts go different distances
            iii. as you increase the value of c, your encoder becomes less accurate
    2. The translation between encoder counts and physical distances is as follows (assuming a speed of "1"):
        a. When moving vertically, 5000 encoder counts will make the arm move ~3 inches
        b. When moving horizontally 5000 encoder counts will make the arm move ~5 inches
        c. This relationship is relatively constant across all multiplicatives of encoder counts
        d. The arm refuses to go more than 16000 encoder counts in one movement, this is accounted for in all movement
            functions.
    3. Latencies
        a. startup to begin communication takes about 32 seconds
        b. at speed "1" the arm takes about 6 seconds to move 16000 encoder counts (~15 inches horizontally and ~9 inches vertically)
'''
'''
global counters to keep track of position while the program is running.  These are relative meaning that all commands will only be useful
if the robot starts at (0,0) when turned on - i.e as far left as possible when facing the back of the pumps, and as far down as it will go
in that position.
'''
xCount = 0
zCount = 0
'''
positions: These are relative to the 0,0 position
'''
xDrink1 = 0 #right at beginning
xDrink2 = 9000 # 7" ahead of 0
xDrink3 = 18000 # 14" ahead of 0, 7" ahead of xDrink2
xDrink4 = 27000 # 21" ahead of 0
xDrink5 = 35000 # 28" ahead of 0
xBlock = 30000

zPump = 28000 #21" above resting point
zBar = 50000 #30" above resting point

xHolder = 30000 #~35" ahead of 0
zHolder = 61000 #37" above resting point

'''
orderList
'''
orderList = [] #need to figure out how to link this with app
sizeList = [] #size list associated with each order

'''
Below are the various movement functions: goX, goZ, goTo, and goHome.  goX and goZ were separated for greater flexibility in determining
when the robot should move vertically or horizontally first. (you don't want the arm moving horizontally while the claw is on the floor)
'''
'''
GoX and goZ each take an encoder count value and move the arm to the corresponding position, using the position information stored in xCount
and zCount respectively.  xCount and zCount are updated as appropriate.  To account for the 16000 encoder count limit, the robot will only 
move that much in one iteration of the while loop if asked to go further than that relative to its current position. goZ has a special
case to account for going to the 0 position.
'''
def goX(x):
    global xCount
    #print "x:", x
    while xCount != x: #until you arrive at the appropriate x position
        #print "Current xCount:", xCount
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
        #print "Final xCount:", xCount
        
def goZ(z):
    global zCount
    #print "z:", z
    while zCount != -z: #repeat for z position
        #print "Current zCount:", zCount
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
        #print "Final zCount:", zCount
        
"""
GoTo takes x and z encoder values and moves to that spot within its work envelope.  the order in which it moves in the x or z directions
depends on whether or not z needs to go down or up
"""
def goTo(x, z):
    global xCount
    global zCount
    if z == 0 or (zCount - z) > 0: #if z is going to move down
        goX(x) #move in the x direction first
        goZ(z)
    else: #otherwise, move up first
        goZ(z)
        goX(x)

"""
goHome mimicks a built in function of the TQ10x controllers, telling the arm to go back to the 0,0 position, in lieu of having some kind of
global counter, ideally, this function would be called before the robot is ever turned off
"""
def goHome(): #go back to zero zero, should do this before turning off
    goTo(0,0)

"""
Below are the functions called while making a drink: newDrink, endDrink, drinkPos,and makeDrink
"""
"""
newDrink takes a drink size (in oz) and grabs a cup from the cup sleeve, lowers to the pump level, and rotates toward the pumps.

To avoid hitting any objects involved in the path the order of operations is:
1. Open claw 
2. Rotate towards cup sleeve
3. Go to the cup sleeve
4. Close claw around cup 
5. Lower to pump level
6. Move back so that you won't hit the shelves when rotating towards the pumps
7. Rotate towards the pumps

This function has code written in it to account for two cup sleeves, one holding 12 oz cups and one holding 24 oz cups. The second sleeve
has not been added to the robot yet, but as long as the size requested doesn't exceed 12, this shouldn't be an issue
"""
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
    goTo(xBlock, zPump) #Go to level of pumps 
    
    #rotate right towards pumps
    gripper_communicator.sendData('L')
    gripper_communicator.sendData('S')

"""
endDrink simply rotates 180 degrees from the last pump that it was at, elevates to the level of the bar on that side, waits 10 seconds for
the customer to grab the drink, and then opens the claw to release the drink, then rotates back to the striaght-forward position.
If the claw is at the 5th pump, it will need to back up before rotating, which is accounted for in this function.
"""
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
    sleep(5) #time to take drink away
    gripper_communicator.sendData('L') #turn back to straight-forward
    gripper_communicator.sendData('S')

"""
Drink Pos uses drink information in a given order to determine which pump to move to and then
goes there
"""
def drinkPos(liquid): #move to drink position, determine based liquid type - want to add code for pumps to work
    x = xDrink1
    if liquid == 1:
        x = xDrink1
    elif liquid == 2:
        x = xDrink2
    elif liquid == 3:
        x = xDrink3
    elif liquid == 4:
        x = xDrink4
    elif liquid == 5:
        x = xDrink5
    goTo(x, zPump)

"""
makeDrink uses the information from an order as input to incorporate the other functions and make a drink, the size parameter is in oz
so the pump_communicator.dispense_ml function is used appropriately (29.5 ml == 1 oz)
"""
def makeDrink(order, size = 12):
    size = int(size)
    newDrink(size)
    for liquid in order: #list of liquids going into drink
        liquid = int(liquid)
        drinkPos(liquid)
        #pump_communicator.dispense_ml(29.5*size/len(order), 200)
    endDrink()

"""
This function, found on stack overflow asks for an input with a time limit on it, this allows us to keep the machine running even while
there aren't any drinks to be made, until we manually tell it to stop.
"""
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

"""
Test() makes the robot go to all of the pump positions and rotate towards the pumps, rotate back straight, and go to (0,0).
Used as proof of concept and to verify each pump position
"""
def Test():
    print "Running test"
    for i in range(1,6): #1-5
        print "Getting drink:", i
        if i == 5:
            goZ(zPump)
            gripper_communicator.sendData('L')
            gripper_communicator.sendData('S')
            drinkPos(i)
        else:
            drinkPos(i) #test going to every position
            gripper_communicator.sendData('L')
            gripper_communicator.sendData('S')
        print "Arrived at position:", i
        sleep(1)
        gripper_communicator.sendData('R')
        gripper_communicator.sendData('S')
        print "Going home"
        goHome()
        print "Home"

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
    MAIN FUNCTION: Go through all of the orders and make the drinks, keep checking the list every 10 seconds for new orders
    """
    kill = ""
    while len(kill) == 0:
        for i in range(len(orderList)):
            if len(sizeList) == 0:
                makeDrink(orderList[i])
            else:
                makeDrink(orderList[i], sizeList[i])
        kill = raw_input_with_timeout("No more drinks in queue, would you like to stop operation?", 10)
    goHome() #we're done for now, go back to the zero-zero position
    
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

