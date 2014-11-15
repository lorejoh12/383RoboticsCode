package main;
import org.python.core.PyInstance;
import org.python.util.PythonInterpreter;

public class BartendroPythonController {
    public static final String DISPENSER_FILE_URL = "./BartendroCode/ui/bartendro/router/driver.py";
    PythonInterpreter interpreter = null;  

    public BartendroPythonController()  
    {  
       PythonInterpreter.initialize(System.getProperties(),  
                                    System.getProperties(), new String[0]);  

       this.interpreter = new PythonInterpreter();  
    }  

    private void execfile( final String fileName )  
    {  
       this.interpreter.execfile(fileName);  
    }  

    private PyInstance createClass( final String className, final String opts )  
    {  
       return (PyInstance) this.interpreter.eval(className + "(" + opts + ")");  
    }  

    public boolean dispense(int pump, double milliliters, int speed){
        
        execfile(DISPENSER_FILE_URL);
        interpreter.set("pump_num", pump);
        double ticks = milliliters*2.54; //TODO whatever the conversion is
        interpreter.set("ticks", ticks);
        interpreter.set("speed", speed);
        
        interpreter.exec("RouterDriver(\"/dev/ttyAMA0\", true).dispense_ticks(pump_num, ticks, speed)");
        
        return true;
    }
    
    public static void main (String[] args){
        BartendroPythonController b = new BartendroPythonController();
        b.dispense(1, 100, 200);
    }
}
