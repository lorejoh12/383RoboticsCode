package main;
import exceptions.CommCommunicationException;
import gnu.io.*;
import java.io.*;
import java.util.*;


public class CommCommunicator{
    static SerialPort serialPort;
    static OutputStream outputStream;
    static InputStream inputStream;
    
    public enum ARM_DIRECTION{
        VERTICAL, HORIZONTAL;

        public int getValue(){
            if( this.equals(ARM_DIRECTION.VERTICAL)){
                return 1;
            }
            else return 2;
        }
    }

    public CommCommunicator() throws CommCommunicationException, InterruptedException
    {
        System.out.println("LOGGING:     INTIALIZING COMMCOMMUNICATOR");
        initializeConnection();
        initializeSettings();
        System.out.println("LOGGING:     COMMCOMMUNICATOR INITIALIZED");
    }
    
    public boolean moveBigArm(int movementCounts, ARM_DIRECTION dir, int velocity) throws InterruptedException{
        String[] commands = {"S", "A5", "V"+velocity, "D"+movementCounts, "G"};
        for(int i = 0; i < commands.length; i++){
            commands[i] = dir.getValue()+commands[i];
        }
        boolean commandsSuccessful = issueCommands(commands);
        Thread.sleep(4000);
        return commandsSuccessful;
    }

    public boolean issueCommands(String[] commands){
        try {
            for(String s : commands){
                outputStream.write((s+"\r").getBytes());
                int carriageReturns = 0;
                int returnByte = 1;
                while(returnByte>=0) { // waits for EOF
                    returnByte =inputStream.read();
                    if (returnByte>=0) System.out.print(Character.toChars(returnByte));
                    if (returnByte==13) carriageReturns++; // counts the number of carriage returns (currently unused)
                }
            }

            return true; // executed successfully
        } catch (IOException | NullPointerException e) {
            return false; // did not execute successfully
        }
    }

    /**
     * Opens the COM ports and tries to initialize connection to TQ10X drivers
     * @return true if initialization successful, false if error was encountered
     */
    private boolean initializeConnection() throws CommCommunicationException
    {
        Enumeration<?> portList = null;
        CommPortIdentifier portId = null;
        portList = CommPortIdentifier.getPortIdentifiers();
        boolean commandsSent = false;
        while (portList.hasMoreElements() && !commandsSent) {
            portId = (CommPortIdentifier) portList.nextElement();
            if (portId.getPortType() == CommPortIdentifier.PORT_SERIAL) {
                if (portId.getName().equals("COM1")) { // TODO this is ridiculous
                    try {
                        serialPort = (SerialPort)
                                portId.open("BartenderCommunicationApp", 2000);
                    } catch (PortInUseException e) {
                        throw new CommCommunicationException("Port is in use. Turn off other apps using this port, then restart Java.");
                    }
                    try {
                        outputStream = serialPort.getOutputStream();
                        inputStream = serialPort.getInputStream();
                        serialPort.setSerialPortParams(9600,
                                                       SerialPort.DATABITS_8,
                                                       SerialPort.STOPBITS_1,
                                                       SerialPort.PARITY_NONE);
                    } catch (UnsupportedCommOperationException| IOException e) {
                        throw new CommCommunicationException("Communication Exception, shutting down");
                    }
                    commandsSent = true;
                }
            }

        }
        if (portId == null) {
            throw new CommCommunicationException("Could not find COM port.");
        }
        
        return true;
    }
    
    /**
     * Used to initialize the settings for the TQ10X drivers. Sets up the addressing on the drivers, the
     * interpretation of the limit switches, and the home driver interpretation. Finally, waits one second
     * to ensure the setup has time to finish.
     * @throws InterruptedException
     */
    private void initializeSettings() throws InterruptedException
    {
        String[] initializationCommands = {"#1", "1OSA1", "2OSA1", "1CEW500", "2CEW500", "A1", "V1", "D0", "INE1"};
        issueCommands(initializationCommands);
        Thread.sleep(1000);
    }

    /**
     * Used to close all IO ports and shut down the program
     */
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
