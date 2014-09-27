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
package org.eclipse.swt.internal.win32;


public class CRYPT_ALGORITHM_IDENTIFIER {
	/** @field cast=(LPSTR) */
	public int /*long*/ pszObjId;
	public CRYPT_OBJID_BLOB Parameters = new CRYPT_OBJID_BLOB ();

	static final public int sizeof = OS.CRYPT_ALGORITHM_IDENTIFIER_sizeof ();
}
