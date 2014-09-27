/*******************************************************************************
 * Copyright (c) 2000, 2013 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.swt.events;

import org.eclipse.swt.internal.*;

/**
 * This listener interface may be implemented in order to receive
 * SegmentEvents.
 * @see SegmentEvent
 *
 * @since 3.8
 */
public interface SegmentListener extends SWTEventListener {

/**
 * This method is called when text content is being modified. 
 * <p>
 * The following event fields are used:<ul>
 * <li>event.lineText text content (input)</li>
 * <li>event.segments text offsets for segment characters (output)</li>
 * <li>event.segmentsChars characters that should be inserted (output, optional)</li>
 * </ul>
 *
 * @param event the given event
 * @see SegmentEvent
 */
public void getSegments(SegmentEvent event);

}
