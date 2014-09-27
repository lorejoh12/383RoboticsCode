
public class MainController 
{
	ArduinoCommunicator ardComm;
	CommCommunicator commComm;
	private int currLocation;
	public MainController()
	{
		commComm = new CommCommunicator();
		ardComm = new ArduinoCommunicator();
		currLocation = 1;
	}
	private void closeGripper(int delay) throws InterruptedException
	{
		ardComm.serialWrite("C");
		Thread.sleep(delay);
	}
	private void openGripper(int delay) throws InterruptedException
	{
		ardComm.serialWrite("O");
		Thread.sleep(delay);
	}
	private void rotateR(int delay) throws InterruptedException
	{
		ardComm.serialWrite("R");
		Thread.sleep(delay);
	}
	private void rotateL(int delay) throws InterruptedException
	{
		ardComm.serialWrite("L");
		Thread.sleep(delay);
	}
	private void endRotate(int delay) throws InterruptedException
	{
		ardComm.serialWrite("S");
		Thread.sleep(delay);
	}
	private void upCup() throws InterruptedException
	{
		commComm.moveToLocation(CommCommunicator.UP_CUP);
		Thread.sleep(4000);
	}
	private void downCup() throws InterruptedException
	{
		commComm.moveToLocation(CommCommunicator.DOWN_CUP);
		Thread.sleep(4000);
	}
	private void allOff()
	{
		ardComm.serialWrite("B");
	}
	
	private void moveToLocation(int nextLocation) throws InterruptedException
	{
		int diff = nextLocation - currLocation;
		if(diff == 0) return;
		if (diff < 0)
		{
			diff = diff * -1;
			commComm.moveToLocation(CommCommunicator.MOVEMENT_LEFT[diff - 1]);
		}
		else
		{
			commComm.moveToLocation(CommCommunicator.MOVEMENT_RIGHT[diff - 1]);			
		}
		currLocation = nextLocation;
		int delay = diff*4000;
		Thread.sleep(delay);
	}
	void setup() throws InterruptedException
	{
		commComm.moveToLocation("XR1\r");
		Thread.sleep(5000);
		
		ardComm.serialWrite("E");
		while (!ardComm.ready){
			Thread.sleep(2000);
		}
	}
	
	private void cupRoutine() throws InterruptedException
	{
		upCup();
		openGripper(2000);
		rotateR(800);
		endRotate(2000);
		downCup();
		closeGripper(2000);
		rotateL(550);
		endRotate(1000);
	}
	private void placeRoutine() throws InterruptedException
	{
		moveToLocation(1);
		upCup();
		rotateR(800);
		endRotate(2000);
		downCup();
		openGripper(2000);
		upCup();
		rotateL(550);
		endRotate(2000);
		downCup();
		allOff();
	}
	
	public void makeDrink(int locations[]) throws InterruptedException
	{
		cupRoutine();
		for(int i = 0; i<locations.length;i++){
			moveToLocation(locations[i]);
			rotateL(12000/(locations.length));
			rotateR(250);
			endRotate(1000);
		}
		placeRoutine();
	}
	
	public static void main(String[] args)
	{
		MainController mc = new MainController();

/*		
		try {

			//A sample movement scheme.  Moves to location 3, rotates arm, then 
//moves to location 2
			mc.setup();
			Thread.sleep(5000);
			mc.moveToLocation(3);
			Thread.sleep(3000);
			mc.openGripper();
			Thread.sleep(2000);
			mc.closeGripper();
			Thread.sleep(2000);
			mc.rotateR();
			Thread.sleep(2000);
			mc.rotateL();
			Thread.sleep(2000);
			mc.ardComm.serialWrite("B");
			Thread.sleep(2000);
			mc.moveToLocation(2);
		} catch (InterruptedException e) {
			mc.ardComm.close();
			mc.commComm.finish();
			// TODO Auto-generated catch block
			e.printStackTrace();
		}*/
		try{
			mc.moveToLocation(1);
			mc.setup();
			int k[] = {3,1,2};
			mc.makeDrink(k);
		} catch (InterruptedException e) {
			mc.ardComm.close();
			mc.commComm.finish();
			e.printStackTrace();
		}
		mc.ardComm.close();
		mc.commComm.finish();

	}
	
	
}
