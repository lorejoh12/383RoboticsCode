import gnu.io.*;

import java.io.*;
import java.util.*;


public class CommCommunicator{
	static Enumeration<?> portList;
	static CommPortIdentifier portId;
	static final String ONE_LEFT = "XR3\r";
	static final String ONE_RIGHT = "XR2\r";
	static final String TWO_LEFT = "XR5\r";
	static final String TWO_RIGHT = "XR4\r";
	static final String DOWN_CUP = "XR7\r";
	static final String UP_CUP = "XR6\r";
	public static final String[] MOVEMENT_LEFT = {
		ONE_LEFT, TWO_LEFT
	};
	public static final String[] MOVEMENT_RIGHT = {
		ONE_RIGHT, TWO_RIGHT
	};

	static SerialPort serialPort;
	static OutputStream outputStream;
	static InputStream inputStream;

	public CommCommunicator()
	{
		System.out.println("LOGGING:     INTIALIZING COMMCOMMUNICATOR");
		initialize();
		System.out.println("LOGGING:     COMMCOMMUNICATOR INITIALIZED");
	}
	public void moveToLocation(String location)
	{
		System.out.println("LOGGING:     MOVING TO LOCATION " + location);
		try {
			outputStream.write(location.getBytes());
			int x = 0;
			int s = 1;
			while(s>=0) {
				s =inputStream.read();
				if (s>=0) System.out.print(Character.toChars(s));
				if (s==13) x++;
			}
		} catch (IOException e) {
			finish();
		}
		System.out.println("LOGGING:     SUCCESSFULLY MOVED TO LOCATION");

	}

	//Opens connection
	public void initialize()
	{
		portList = CommPortIdentifier.getPortIdentifiers();
		boolean commandsSent = false;
		while (portList.hasMoreElements() && !commandsSent) {
			portId = (CommPortIdentifier) portList.nextElement();
			if (portId.getPortType() == CommPortIdentifier.PORT_SERIAL) {
				if (portId.getName().equals("COM3")) {
					try {
						serialPort = (SerialPort)
								portId.open("SimpleWriteApp", 2000);
					} catch (PortInUseException e) {
						System.out.print("WHAT?");
						this.finish();
						e.printStackTrace();
					}
					try {
						outputStream = serialPort.getOutputStream();
						inputStream = serialPort.getInputStream();
					} catch (IOException e) {}
					try {
						serialPort.setSerialPortParams(9600,
								SerialPort.DATABITS_8,
								SerialPort.STOPBITS_1,
								SerialPort.PARITY_NONE);
					} catch (UnsupportedCommOperationException e) {
						this.finish();
					}
					commandsSent = true;
				}
			}

		}
		if (portId == null) {
			System.out.println("Could not find COM port.");
			return;
		}


	}

	public void finish()
	{
		serialPort.close();
		System.out.println("LOGGING:      COMMCOMMUNICATOR CLOSED");
		try {
			outputStream.close();
			inputStream.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
