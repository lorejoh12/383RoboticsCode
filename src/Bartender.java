import java.util.ArrayList;
import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;

//Bartender User Interface:

public class Bartender {
	public static int APPLE = 3;
	public static int CRANBERRY = 2;
	public static int ORANGE = 1;

	protected Shell shell;
	protected static MainController mc;

	/**
	 * Launch the application
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		try {
			mc = new MainController();

			// call setup routine to move robot arm to home position (from
			// ground level to bar level)
			mc.setup();

			// Create and launch application
//			Bartender window = new Bartender();
//			window.open();
			
			mc.finish();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * Open the window.
	 */
	public void open() {
		Display display = Display.getDefault();
		createContents();
		shell.open();
		shell.layout();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) {
				display.sleep();
			}
		}
	}

	/**
	 * Create contents of the window.
	 */
	protected void createContents(){
		shell = new Shell();
		shell.setSize(450,374);
		shell.setText("SWT Application");

		Label lblWelcomeToThe = new Label(shell, SWT.NONE); 
		lblWelcomeToThe.setFont(SWTResourceManager.getFont("Tahoma", 16, SWT.NORMAL));
		lblWelcomeToThe.setBounds(27, 10, 405, 25);
		lblWelcomeToThe.setText("WELCOME TO THE BARTENDER ROBOT!");
		Group grpPleaseSelectYour = new Group(shell, SWT.NONE);
		grpPleaseSelectYour.setText("Please select your ingredients...");
		grpPleaseSelectYour.setBounds(10, 48, 302, 128);

		Group grpPleaseSelectYour_1 = new Group(shell, SWT.NONE);
		final Button btnCheckButton = new Button(grpPleaseSelectYour_1, SWT.CHECK);
		final Button btnEverything  = new Button(grpPleaseSelectYour_1, SWT.CHECK);
		final Button btnSurpriseMe  = new Button(grpPleaseSelectYour_1, SWT.CHECK);
		final Button btnAppleJuice  = new Button(grpPleaseSelectYour_1, SWT.CHECK);

		btnAppleJuice.setBounds(10, 22, 93, 16);
		btnAppleJuice.setText("Sprite");

		final Button btnCranberryJuice = new Button(grpPleaseSelectYour, SWT.CHECK);
		btnCranberryJuice.setBounds(10, 56, 110, 16);
		btnCranberryJuice.setText("Cranberry juice");

		final Button btnOrangeJuice = new Button(grpPleaseSelectYour, SWT.CHECK);
		btnOrangeJuice.setBounds(10, 91, 93, 16);
		btnOrangeJuice.setText("Orange Juice");

		Button btnOrderDrink = new Button(shell, SWT.NONE);
		btnOrderDrink.addMouseListener(new MouseAdapter(){
			@Override
			public void mouseDown(MouseEvent e){
				// Read status of all checkboxes to determine user selection

				boolean apple = btnAppleJuice.getSelection();
				boolean cranberry = btnCranberryJuice.getSelection();
				boolean orange = btnOrangeJuice.getSelection();
				boolean janet = btnCheckButton.getSelection();
				boolean eve = btnEverything.getSelection();
				boolean sur = btnSurpriseMe.getSelection();
				List<Integer> selectionsList = new ArrayList<Integer>();

				// Add appropriate ingredients based on user selections
				if(orange){
					selectionsList.add(ORANGE);
				}
				if(cranberry){
					selectionsList.add(CRANBERRY);
				}
				if(apple){
					selectionsList.add(APPLE);
				}
				if(janet){
					selectionsList.add(ORANGE);
					selectionsList.add(CRANBERRY);
				}
				if(eve){
					selectionsList.add(ORANGE);
					selectionsList.add(CRANBERRY);
					selectionsList.add(APPLE);
				}
				if(sur){
					apple = (Math.random() < 0.5);
					cranberry = (Math.random() < 0.5);
					orange = (Math.random() < 0.5);
					if(orange){
						selectionsList.add(ORANGE);
					}
					if(cranberry){
						selectionsList.add(CRANBERRY);
					}
					if(apple){
						selectionsList.add(APPLE);
					}
				}
				int[] selections = new int[selectionsList.size()];
				for(int i = 0; i < selections.length; i++){
					selections[i] = selectionsList.get(i);
					System.out.println("Selection = " + selections[i]);
				}

				// Pass array of drink IDs to MainController and make the drink

				try{
					mc.makeDrink(selections);
				} catch(InterruptedException e1){
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		btnOrderDrink.setBounds(327, 97, 105, 56);
		btnOrderDrink.setText("ORDER DRINK");

		Button exitButton = new Button(shell, SWT.NONE);
		exitButton.addMouseListener(new MouseAdapter(){
			@Override
			public void mouseDown(MouseEvent e){
				//Turn off communication with Arduino that controls wrist and gripper motion
				mc.ardComm.close();
				mc.commComm.finish();
			}
		});

		exitButton.setBounds(333, 203, 99, 56);
		exitButton.setText("Exit");

		grpPleaseSelectYour_1.setText("Please select your drink special...");
		grpPleaseSelectYour_1.setBounds(10, 216, 302, 110);

		/*
		 * The following SelectionListeners ensure that options that need
		 * to be mutually exclusive (i.e. user can't select 'Everything'
		 * and 'Orange Juice' or 'Everything' and 'Surprise Me')
		 */

		btnAppleJuice.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnAppleJuice.getSelection()){
					btnCheckButton.setSelection(false);
					btnEverything.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});

		btnCranberryJuice.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnCranberryJuice.getSelection()){
					btnCheckButton.setSelection(false);
					btnEverything.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});

		btnOrangeJuice.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnOrangeJuice.getSelection()){
					btnCheckButton.setSelection(false);
					btnEverything.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});

		btnCheckButton.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnCheckButton.getSelection()){
					btnAppleJuice.setSelection(false);
					btnCranberryJuice.setSelection(false);
					btnOrangeJuice.setSelection(false);
					btnEverything.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});

		btnEverything.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnEverything.getSelection()){
					btnAppleJuice.setSelection(false);
					btnCranberryJuice.setSelection(false);
					btnOrangeJuice.setSelection(false);
					btnCheckButton.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});

		btnSurpriseMe.addSelectionListener(new SelectionAdapter(){
			@Override
			public void widgetSelected(SelectionEvent e){
				if(btnSurpriseMe.getSelection()){
					btnAppleJuice.setSelection(false);
					btnCranberryJuice.setSelection(false);
					btnOrangeJuice.setSelection(false);
					btnEverything.setSelection(false);
					btnSurpriseMe.setSelection(false);
				}
			}
		});
		btnCheckButton.setBounds(10, 22, 85, 16);
		btnCheckButton.setText("Janet Special");

		btnEverything.setBounds(10, 54, 85, 16);
		btnEverything.setText("Everything");

		btnSurpriseMe.setBounds(10, 84, 85, 16);
		btnSurpriseMe.setText("Surprise Me!");

		Label lblOr = new Label(shell, SWT.NONE);
		lblOr.setFont(SWTResourceManager.getFont("Tahoma", 12, SWT.BOLD));
		lblOr.setBounds(122, 185, 59, 28);
		lblOr.setText("--OR--");
	}
}