/*******************************************************************************
 * Copyright (c) 2010, 2012 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.swt.internal.webkit;


import org.eclipse.swt.internal.ole.win32.*;

public class IWebPolicyDecisionListener extends IUnknown{

public IWebPolicyDecisionListener (int /*long*/ address) {
	super (address);
}

public int use () {
	return COM.VtblCall (3, getAddress ());
}

public int download () {
	return COM.VtblCall (4, getAddress ());
}

public int ignore () {
	return COM.VtblCall (5, getAddress ());
}

}
