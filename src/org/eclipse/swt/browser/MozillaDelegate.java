/*******************************************************************************
 * Copyright (c) 2005, 2010 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.swt.browser;

import org.eclipse.swt.browser.Browser;
import org.eclipse.swt.internal.Callback;
import org.eclipse.swt.internal.mozilla.*;
import org.eclipse.swt.internal.win32.*;
import org.eclipse.swt.widgets.*;

class MozillaDelegate {
	Browser browser;
	static long /*int*/ MozillaProc;
	static Callback SubclassProc;
	
MozillaDelegate (Browser browser) {
	super ();
	this.browser = browser;
}

static Browser findBrowser (long /*int*/ handle) {
	Display display = Display.getCurrent ();
	return (Browser)display.findWidget (handle);
}

static String getLibraryName () {
	return "xpcom.dll"; //$NON-NLS-1$
}

static char[] mbcsToWcs (String codePage, byte[] buffer) {
	char[] chars = new char[buffer.length];
	int charCount = OS.MultiByteToWideChar (OS.CP_ACP, OS.MB_PRECOMPOSED, buffer, buffer.length, chars, chars.length);
	if (charCount == chars.length) return chars;
	char[] result = new char[charCount];
	System.arraycopy (chars, 0, result, 0, charCount);
	return result;
}

static byte[] wcsToMbcs (String codePage, String string, boolean terminate) {
	int byteCount;
	char[] chars = new char[string.length()];
	string.getChars (0, chars.length, chars, 0);
	byte[] bytes = new byte[byteCount = chars.length * 2 + (terminate ? 1 : 0)];
	byteCount = OS.WideCharToMultiByte (OS.CP_ACP, 0, chars, chars.length, bytes, byteCount, null, null);
	if (terminate) {
		byteCount++;
	} else {
		if (bytes.length != byteCount) {
			byte[] result = new byte[byteCount];
			System.arraycopy (bytes, 0, result, 0, byteCount);
			bytes = result;
		}
	}
	return bytes;
}

static long /*int*/ windowProc (long /*int*/ hwnd, long /*int*/ msg, long /*int*/ wParam, long /*int*/ lParam) {
	switch ((int)/*64*/msg) {
		case OS.WM_ERASEBKGND:
			RECT rect = new RECT ();
			OS.GetClientRect (hwnd, rect);
			OS.FillRect (wParam, rect, OS.GetSysColorBrush (OS.COLOR_WINDOW));
			break;
	}
	return OS.CallWindowProc (MozillaProc, hwnd, (int)/*64*/msg, wParam, lParam);
}

void addWindowSubclass () {
	long /*int*/ hwndChild = OS.GetWindow (browser.handle, OS.GW_CHILD);
	if (SubclassProc == null) {
		SubclassProc = new Callback (MozillaDelegate.class, "windowProc", 4); //$NON-NLS-1$
		MozillaProc = OS.GetWindowLongPtr (hwndChild, OS.GWL_WNDPROC);
	}
	OS.SetWindowLongPtr (hwndChild, OS.GWL_WNDPROC, SubclassProc.getAddress ());
}

int createBaseWindow (nsIBaseWindow baseWindow) {
	return baseWindow.Create ();
}

long /*int*/ getHandle () {
	return browser.handle;
}

String getJSLibraryName () {
	return "js3250.dll"; //$NON-NLS-1$
}

String getProfilePath () {
	String baseDir;
	/* Use the character encoding for the default locale */
	TCHAR buffer = new TCHAR (0, OS.MAX_PATH);
	if (OS.SHGetFolderPath (0, OS.CSIDL_APPDATA, 0, OS.SHGFP_TYPE_CURRENT, buffer) == OS.S_OK) {
		baseDir = buffer.toString (0, buffer.strlen ());
	} else {
		baseDir = System.getProperty("user.home"); //$NON-NLS-1$
	}
	return baseDir + Mozilla.SEPARATOR_OS + "Mozilla" + Mozilla.SEPARATOR_OS + "eclipse"; //$NON-NLS-1$ //$NON-NLS-2$
}

String getSWTInitLibraryName () {
	return "swt-xulrunner"; //$NON-NLS-1$
}

void handleFocus () {
}

void handleMouseDown () {
}

boolean hookEnterExit () {
	return true;
}

void init () {
}

boolean needsSpinup () {
	return false;
}

void onDispose (long /*int*/ embedHandle) {
	removeWindowSubclass ();
	browser = null;
}

void removeWindowSubclass () {
	if (SubclassProc == null) return;
	long /*int*/ hwndChild = OS.GetWindow (browser.handle, OS.GW_CHILD);
	OS.SetWindowLongPtr (hwndChild, OS.GWL_WNDPROC, MozillaProc);
}

boolean sendTraverse () {
	return false;
}

void setSize (long /*int*/ embedHandle, int width, int height) {
}
}
