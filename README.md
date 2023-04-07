# How to use this script:

* Use Google Chrome
* Login to Clarizen manually
  * Log into Clarizen https://app2.clarizen.com/Clarizen/Pages/Service/Login.aspx?ReturnUrl=%2fClarizen%2fTask%2f16972537857
* Get the cookies you need for this script
  * On the Clarizen webpage in the Chrome browser, right click and select "inspect"
  * A side bar should appear with lot of info
  * Click "Network" on the top menu of the side bar (after "Elements", "Console", etc.)
  * A few rows below, select the "Fetch/XHR" option (besides the "All" option)
  * On the Clarizen page, click the Tasks icon (on the left vertical menu)
  * You'll see a lot of records populate in the "inspect" sidebar.
  * Select one that starts with "Ajax?..."
  * Right click -> Copy -> Copy as cURL
  * Go to https://curlconverter.com/ and make sure Python is selected
  * Paste the cURL command, you'll see translated Python code
  * In the cookies dictionary, copy the bottom five rows. They should match the ones in the get_cookies function below
  * Paste them into the cookies dictionary in the code below (overwriting what's there)
* Run the script: python3 clarizen_scraper.py

# How files are stored:
- Files are stored in the same directory as the script in a "downloads" folder
- Sub folders are named with the Clarizen task id so we can reference the task later

# What if the script crashes:
- Just start it again, it checks if the Clarizen task has been checked already
  (by looking at the downloads folder)

# What if the user name / password expires:
- Do the 1,2,3 steps again and get new cookies

# Slack John Wang if you have problems


# Misc

No login. You have to manually login. Grab an XHR request.
And get the 4 cookies that matter that are set from that request.
Those cookies are set in the get_cookies() function as the initial
set of cookies.
Once that's updated, the script is ready to go.

1. Script goes through static list of task ids (pre-fetched)
2. For each task, check if it's approved
3. If approved, fetch all files
4. Once files gets above certain count, we download them
