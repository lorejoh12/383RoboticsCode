
public class MainController 
{
	ArduinoCommunicator ardComm;
	CommCommunicator commComm;
	private int currLocation;
	public MainController()
	{
		commComm = new CommCommunicator();
		try {
			ardComm = new ArduinoCommunicator();
		} catch (Exception e) {
			commComm.finish();
			e.printStackTrace();
		}
		currLocation = 1;
	}
	private void closeGripper(int delay) throws Exception
	{
		ardComm.serialWrite("C");
		Thread.sleep(delay);
	}
	private void openGripper(int delay) throws Exception
	{
		ardComm.serialWrite("O");
		Thread.sleep(delay);
	}
	private void rotateR(int delay) throws Exception
	{
		ardComm.serialWrite("R");
		Thread.sleep(delay);
	}
	private void rotateL(int delay) throws Exception
	{
		ardComm.serialWrite("L");
		Thread.sleep(delay);
	}
	private void endRotate(int delay) throws Exception
	{
		ardComm.serialWrite("S");
		Thread.sleep(delay);
	}
	private void upCup() throws Exception
	{
		commComm.moveToLocation(CommCommunicator.UP_CUP);
		Thread.sleep(4000);
	}
	private void downCup() throws Exception
	{
		commComm.moveToLocation(CommCommunicator.DOWN_CUP);
		Thread.sleep(4000);
	}
	private void allOff() throws Exception
	{
		ardComm.serialWrite("B");
	}
	
	private void moveToLocation(int nextLocation) throws Exception
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
		commComm.moveToLocation("XR2\r");
		Thread.sleep(5000);
		commComm.moveToLocation("XR3\r");
		Thread.sleep(5000);
		commComm.moveToLocation("XR4\r");
		Thread.sleep(5000);
		commComm.moveToLocation("XR5\r");
		Thread.sleep(5000);
		commComm.moveToLocation("XR6\r");
		Thread.sleep(5000);
		commComm.moveToLocation("XR7\r");
		
//		ardComm.serialWrite("E");
//		while (!ardComm.ready){
//			Thread.sleep(2000);
//		}
	}
	
	private void cupRoutine() throws Exception
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
	private void placeRoutine() throws Exception
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
	
	public void makeDrink(int locations[]) throws Exception
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
		} catch (Exception e) {
			mc.ardComm.close();
			mc.commComm.finish();
			e.printStackTrace();
		}
		mc.ardComm.close();
		mc.commComm.finish();

	}
	
	public void finish(){
		commComm.finish();
	}
	
	
}
