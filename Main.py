'''
Created on Nov 13, 2014

This is the main class for controlling the ECE383 Bartender Robot.
It is porting the serial communication used in past projects over into
python

@author: John Lorenz
@author: Brad Levergood
'''

from time import sleep
import CommCommunicator
import PumpCommunicator
import GripperCommunicator
import UnoCommunicator
import math
import random
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
            i.   "c" can be any value between 0 and an upper limit determined by the constant acceleration value of 5 m/s^2 of the arm
            ii.  Different speeds make the encoder counts go different distances
            iii. As you increase the value of c, your encoder becomes less accurate
            iv. At the moment, the speed of the arm is set by the speed variable below which is being used for all moveArm() calls, changing this
                variable will change the speed at which the robotic arm makes all of its movements
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
speed = 1
xDrink1 = 0 #right at beginning
xDrink2 = 7500 # 7" ahead of 0
xDrink3 = 16500 # 14" ahead of 0, 7" ahead of xDrink2
xDrink4 = 24500 # 21" ahead of 0
xDrink5 = 33000 # 28" ahead of 0
xBlock = 30000

zPump = 27000 #21" above resting point
zDone = 50000 #30" above resting point
zBar = 35000

xHolder = 30000 #~35" ahead of 0
zHolder = 47000 #37" above resting point


'''
Below are the various movement functions: goX, goZ, goTo, and goHome.  goX and goZ were separated for greater flexibility in determining
when the robot should move vertically or horizontally first. (you don't want the arm moving horizontally while the claw is on the floor)
'''
'''
GoX and goZ each take an encoder count value and move the arm to the corresponding position, using the position information stored in xCount
and zCount respectively.  xCount and zCount are updated as appropriate.  The robotic arm does not like to go more than 16000 encoder counts 
in any direction at one time.  To account for the 16000 encoder count limit, the robot will only  move that much in one iteration of the 
while loop if asked to go further than that relative to its current position. goZ also has a special case to account for going to the 
0 position.
'''
def goX(x):
    global xCount
    #print "x:", x
    while xCount != x: #until you arrive at the appropriate x position
        #print "Current xCount:", xCount
        if math.fabs(x-xCount) > 16000:
            if x-xCount > 0:
                comm_communicator.moveArm(16000, 2, speed)
                xCount += 16000
            else:
                comm_communicator.moveArm(-16000, 2, speed)
                xCount -= 16000
        else:
            comm_communicator.moveArm(x-xCount, 2, speed) #move the arm the correct encoder difference
            xCount += (x-xCount)# this will be positive or negative based on your position which you keep track of while the robot is on
        #print "Final xCount:", xCount
        
def goZ(z):
    global zCount
    #print "z:", z
    while zCount != -z: #repeat for z position
        #print "Current zCount:", zCount
        if z == 0:
            if math.fabs(-zCount) > 16000:
                comm_communicator.moveArm(16000, 1, speed)
                zCount += 16000
            else:
                comm_communicator.moveArm(-zCount, 1 , speed)
                zCount = 0
        else:
            if math.fabs(zCount + z) > 16000:
                if (-zCount) < z:
                    comm_communicator.moveArm(-16000, 1, speed)
                    zCount  -= 16000
                else:
                    comm_communicator.moveArm(16000, 1, speed)
                    zCount += 16000
            else:
                comm_communicator.moveArm(-1*(zCount + z), 1, speed)
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
global counter, ideally, this function would be called before the robot is ever turned off, and this is how it is currently implemented.
For calibration purposes, since there is a motion limiter on the negative-x direction of the robot, the robot is actually asked to move to -500
in the x direction, guaranteeing that it will stop at the 0 point.  It's xCount value is then manually set to 0
"""
def goHome(): #go back to zero zero, should do this before turning off
    goTo(-500,0)
    xCount = 0

"""
Below are the functions called while making a drink: newDrink, endDrink, drinkPos,and makeDrink
"""
"""
newDrink takes a drink size (in oz) and grabs a cup from the cup sleeve, lowers to the pump level, and rotates toward the pumps.

To avoid hitting any objects involved in the path the order of operations is:
1. Open claw 
2. Go to the farthest point in the x-direction without being able to hit the shelves
3. Rotate towards the empty bar to receive an empty cup
4. wait 10 seconds for somebody to give the claw the cup
5. Close claw around cup 
6. Straighten out
7. Lower to the level of the pumps
8. Turn towards the pumps

This function has code written in it to account for two cup sleeves, one holding 12 oz cups and one holding 24 oz cups. The second sleeve
has not been added to the robot yet, and due to some minor difficulties, we do not currently incorporate the sleeves into our process.
This is a good area for future groups to develop.
"""
def newDrink(size): 
    gripper_communicator.sendData('O')#open before arriving at cup
    
    # if int(size) <= 12 and int(size) > 0: #--> rotation code for different sleeves
        # gripper_communicator.sendData('L')
        #gripper_communicator.sendData('S')
    # elif int(size) <= 24 and int(size) > 12:
        # gripper_communicator.sendData('R') #rotate arm toward larger sleeve
        # gripper_communicator.sendData('S')
        
    # goTo(xHolder, zHolder) #go to cup sleeve with open, rotated claw

    goTo(xBlock, zBar)
    gripper_communicator.sendData('F') #go to bar opposite pumps to recieve cup
    sleep(10) #wait 10 seconds to recieve cup
    gripper_communicator.sendData('C') #close claw around cup
    sleep(2) #take hand away
    gripper_communicator.sendData('S') #straighten out to lower
    goTo(xBlock, zPump) #Go to level of pumps
    gripper_communicator.sendData('B') #face pumps

"""
endDrink straightens out the claw from the last pump that it was at, elevates very high upwards (given to the zDone variable),
rotates towards the empty bar, lowers towards the level of the bar, placing the cup on it, waits 10 seconds for the customer 
to grab the drink, and then opens the claw to release the drink, waits 5 seconds for the customer to take the cup away, then 
rotates back to the straight-forward position. If the claw is at the 5th pump, it will need to back up before rotating, 
which is accounted for in this function.
"""
def endDrink(): #give finished drink to customer, bar opposite the pumps
    if xCount > xBlock: #make sure you can rotate (i.e. you're last liquid wasn't 5)
        goX(xBlock)
    gripper_communicator.sendData('S') #Straighten out to elevate
    goZ(zDone)
    gripper_communicator.sendData('F') #face other end of bar
    goZ(zBar)
    sleep(10) # Give user 10 seconds to grab onto drink
    gripper_communicator.sendData('O') #release the cup
    sleep(5) #time to take drink away
    gripper_communicator.sendData('S') #turn back to straight-forward

"""
DrinkPos uses drink information in a given order to determine which pump to move to and then
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
so the pump_communicator.dispense_ml function is used appropriately (29.5 ml == 1 oz).  In order to synchronize pump function and claw
movement, the function waits for a "False" output to be sent from a given pump's is_dispensing(port) method before moving the claw to
the next pump. The is_dispensing function uses pump ID's internal to the PumpCommunicator class, getting these ID's requires doing a
guess-and-check-type search method (lines 241-245) to check pumping status (line 250).  There is also a check to make sure you never
up in an endless loop in the off-chance that you aren't able to identify the correct pump port.
"""
def makeDrink(order, size = 12):
    size = int(size)
    newDrink(size)
    for liquid in order: #list of liquids going into drink
        liquid = int(liquid)
        dispenser = pump[liquid - 1] - 1
        port = -1
        for i in range(len(pump_communicator.dispenser_ports)):
            if pump_communicator.dispenser_ports[i] == dispenser:
                port = i
        drinkPos(liquid)
        pump_communicator.dispense_ml(pump[liquid-1], 29.5*float(size)/float(len(order)), 200)
        counter = 0
        print "pump:",pump[liquid-1]
        print "port:", port
        while pump_communicator.is_dispensing(port)[0]:
            if counter == 2000:
                print "Endless loop"
                break    
            counter+=1
        sleep(1)
    endDrink()

"""
Test() makes the robot go to all of the pump positions rotate towards the pumps,
straighten back out, and go back to (0,0).
Used as proof of concept and to verify each pump position
"""
def Test():
    print "Running test"
    for i in range(1,6): #1-5
        print "Getting drink:", i
        if i == 5:
            goZ(zPump)
            gripper_communicator.sendData('B')
            drinkPos(i)
        else:
            drinkPos(i) #test going to every position
            gripper_communicator.sendData('B')
        print "Arrived at position:", i
        sleep(1)
        gripper_communicator.sendData('S')
        print "Going home"
        goHome()
        print "Home"
"""
TestRand(its) takes an integer and for as many times as that value determines, it makes drinks using three random
liquids.
"""
def TestRand(its):
    for i in range(its):
        a = random.randint(1,6)#this gets all values between 1-5 (cuts off top value)
        b = random.randint(1,6)
        c = random.randint(1,6)
        print "Iteration:",i
        print "Making Drink:",[a,b,c]
        makeDrink([a,b,c],12)

pump_device = '/dev/ttyAMA0' # the GPIO serial port on the RPI
USB_devices = [ '/dev/tty.PL2303-00001014', '/dev/tty.PL2303-00002014','/dev/tty.usbmodem1411', '/dev/tty.usbmodem1421', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
               '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
pump = [1, 2, 3, 6, 7]

BAUD_RATE = 9600


if __name__ == '__main__':
    comm_communicator = CommCommunicator.CommCommunicator(USB_devices)
    comm_communicator.open()
    pump_communicator = PumpCommunicator.RouterDriver(pump_device, False)
    pump_communicator.open()
    gripper_communicator = GripperCommunicator.GripperCommunicator(USB_devices)
    gripper_communicator.open()
    uno_communicator = UnoCommunicator.UnoCommunicator(USB_devices)
    uno_communicator.open()
    """
    MAIN FUNCTION:
    This is what is actually executed when this module is run.  Comment it out and uncomment the
    code in the testing section to enable user-input usage of the robot.
    
    The algorithm for the main assumes that the user doesn't have access to the Raspberry Pi
    Raspbian OS and is as follows:
    1. On startup, elevate 1000 encoder counts, signaling that it is listen for bluetooth input from the uno_communicator
    2. If the bluetooth app sends a 0, stop operation
    3. If the app sends an "H", send the arm to the 0, 0 position
    4. otherwise look for a string of the following input, digits in the range 1-5 separated by spaces, with the final character being
        a "*"
        a. If the input is invalid, keep waiting for valid input
        b. If the input is valid, make a 12oz drink divided even among each digit in the order
        representing the mixture sequence of liquids sent by the order
    Since the method is written to check the bluetooth input once per iteration of its whileloop
    drinks can be queued together by being stored in the devices buffer until it is grabbed by this readData method
    """
    kill = ""
    makeDrink([1,2,3,4,5], 12) #priming function - pump ~ 2oz in each pump to make sure that each pump is filled
    goZ(1000)
    subDigit = "12345"
    while kill != "0":
        c = uno_communicator.readData();
        if "0" in c:
            kill = "0"
        elif c == "H":
            goHome()
        else:
            valid = 0
            orderStr = c
            print "Data recieved:", orderStr
            order = orderStr[0:orderStr.find("*")].strip().split()
            for o in order:
                if len(o) != 1:
                    valid = -1
                    break
                elif o in subDigit:
                    valid += 1
            if valid == len(order) and orderStr.count(" ") != len(orderStr) and len(order) != 0:
                makeDrink(order, 12)
    goHome()

        
    """
    TEST SECTION - comment out the MAIN FUNCTION code above and uncomment this code below to run user-input operation of the machine
    """

    '''
    Below is a test loop to take commands, input commands as method name and parameters separated by spaces variables may be passed 
    in via a dictionary mapping them to the correct values in the program
    
    issuable commands:
    1.  goto x y: goTo(x,y)
    2.  gox x: goX(x)
    3.  goz z: goZ(z)
    4.  drink i: drinkPos(i)
    5.  new: newDrink(12)
    6.  end: endDrink()
    7.  test: Test()
    8.  rand i: TestRand(i)  
    9.  print: print the encoder count values 
    10. make size liquid1 liquid2...liquidn: makeDrink([liquid1...], size)
    11. pump i size: pump_communicator.dispense(pump[i-1], size, 200) 
    12. claw word: gripper_communicator.sendData(dVals[word])
    13. speed i: speed = i
    14. done: stops the program
    
    Assumptions:
    1. goto will be followed by 2 values, either variable names or encoder values
    2. gox, goz, drink, rand, and claw will be followed by one value
        a. claw's "value" will be "forward", "back", "straight", "open", or "close"
            i.   "forward" turns the claw toward the empty bar
            ii.  "back" turns the claw toward the pumps
            iii. "straight" straightens out the claw 
        b. gox and goz will be followed by either variable names or encoder values
        c. drink will be followed by a number between 1 and 5, signifying a drink position
    3. new, end, test, print, and done will be followed by no values
    4. make will be followed by at least 2 values, the size and the liquid(s) that will go into the drink
    5. pump will be followed by 2 values, the pump to engage (1-5), and the amount of liquid to be dispensed(in oz)
    6. speed will be followed by one value
    '''
#     dVals = {"xcount":xCount, "zcount":zCount, "xdrink1":xDrink1, "xdrink2":xDrink2, "xdrink3":xDrink3, "xdrink4":xDrink4, "xdrink5":xDrink5, "xblock": xBlock, "xholder":xHolder, "zpump":zPump, "zdone":zDone, "zbar":zBar, "zholder":zHolder, "open":'O', "close":'C', "straight":'S', "forward":'F', "back":'B'}
#     comDrink = []
#     comSize = 12
#     comX = 0
#     comZ = 0
#     run = True
#     while run:
#         command = raw_input("Command: ")
#         params = command.split()
#         if params[0] == "done":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 goHome()
#                 run = False
#         elif params[0].lower == "home":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 goHome() 
#         elif params[0].lower() == "test":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 Test()
#         elif params[0].lower() == "rand":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 TestRand(int(params[1]))
#         elif params[0].lower() == "goto":
#             if len(params) != 3:
#                 print "Not a valid command"
#             else:
#                 if params[1].lower() in dVals:
#                     comX = dVals[params[1]]
#                 else:
#                     comX = int(params[1])
#                 if params[2].lower() in dVals:
#                     comZ = dVals[params[2]]
#                 else:
#                     comZ = int(params[2])
#                 goTo(comX,comZ)
#         elif params[0].lower() == "gox":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 if params[1].lower() in dVals:
#                     comX = dVals[params[1]]
#                 else:
#                     comX = int(params[1])
#                 goX(comX)
#         elif params[0].lower() == "goz":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 if params[1].lower() in dVals:
#                     comZ = dVals[params[1]]
#                 else:
#                     comZ = int(params[1])
#                 goZ(comZ)
#         elif params[0].lower() == "new":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 newDrink(12)
#         elif params[0].lower() == "end":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 endDrink()
#         elif params[0].lower() == "drink":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 drinkPos(int(params[1]))
#         elif params[0].lower() == "claw":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 gripper_communicator.sendData(dVals[params[1]])
#         elif params[0].lower() == "print":
#             if len(params) != 1:
#                 print "Not a valid command"
#             else:
#                 print "xCount:", xCount
#                 print "zCount:", zCount
#         elif params[0] == "make":
#             if len(params) < 3:
#                 print "Not a valid command"
#             else:
#                 comSize = params[1]
#                 for i in range(len(params[2:])):
#                     comDrink.append(int(params[i+2]))
#                 makeDrink(comDrink, comSize)
#         elif params[0] == "pump":
#             if len(params) != 3:
#                 print "Not a valid command"
#             else:
#                 pump_communicator.dispense_ml(pump[int(params[1])-1], 29.5*float(params[2]), 200)
#         elif params[0] == "speed":
#             if len(params) != 2:
#                 print "Not a valid command"
#             else:
#                 speed = params[1]
#         else:
#             print "Not a valid command"
        
                
    comm_communicator.close()
    pump_communicator.close()
    gripper_communicator.close()
    uno_communicator.close()

