/*******************************************************************************
 * Copyright (c) 2010, 2011 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.swt.internal.win32;

public class GESTURECONFIG {
	public int dwID;                     // gesture ID
    public int dwWant;                   // settings related to gesture ID that are to be turned on
    public int dwBlock;                  // settings related to gesture ID that are to be turned off
    public static final int sizeof = OS.GESTURECONFIG_sizeof ();
}
