# How to use this script:

* Set environment variables in your terminal
  * `export CLARIZEN_USERNAME='user-name'`
  * `export CLARIZEN_PASSWORD='password'`
* Run the script: `python3 clarizen_scraper.py`

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
