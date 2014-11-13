Release notes for the beta version of 2014-04-8
===============================================

This is our first post-kickstarter software release. We've added a few critical new features, improved
the UI and added support for the new V3 Dispensers that will be shipping soon. 

We've made the changes listed below. If you would like to try out these changes, please see our upgrade
instructions:

https://github.com/partyrobotics/bartendro/blob/master/docs/beta-release-20140408.md

User facing features:

- We've added a "I'm feeling lucky button"
- UI consistency improvements: General improvements. Green buttons indicate that some action will occur when pressing this button!
- Minor UI tweaks and layout improvements
- Improved Shots UI, including allowing users to switch between cocktail and shot mode
- Improved trending drinks menu, giving a view of the last 12 hours, 3 days, 1 week and all time. Drinks are now clickable links to allow users to examine the drinks on the drink screen.
- For dispensing small amounts of liquids, turn the pumps slower for more accurate dispensing

Admin facing features:

- Bartendro logo goes to admin screen
- Taster button on drink designer -- this is really handy for making new drink recipes.
- Improved clean cycle that runs all pumps for 15 seconds. Bartendro 15 can clean the pumps on the left side indepdenently from the pumps on the right side.
- Rewritten Bartendro Mixer, which is the heart of Bartendro. This should fix a number of liquid level bugs and give better overall stability
- If v3 dispensers are installed, then a "reverse" button appears on the dispenser admin page.
- Display network IP addresses that Bartendro has on the options screen
- Added an option wether or not to show the shots interface.
- Added an option wether or not to show the "I'm feeling lucky!" button
- Used better visual cues in the dispenser view to show the liquid level for each dispenser (if enabled)
- Improved wording of the database upload/download feature

Firmware changes:

- Created updated firmware for v3 Dispensers.
- v3 Dispensers will be able to run pumps in both directions.
- Implemented version checking in firmware

Issues fixed in this release
----------------------------

The following issues have been closed for this release:

https://github.com/partyrobotics/bartendro/issues?milestone=3&page=1&state=closed

Issues still open before release:

https://github.com/partyrobotics/bartendro/issues?milestone=3&state=open

If you find any problems with this release, please report them here:

https://github.com/partyrobotics/bartendro/issues/new
