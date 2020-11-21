"""
Configuration file for the Coronavirus website scraper's main code
"""

# The URL to fetch data from
URL = "https://www.worldometers.info/coronavirus/"

# Columns names block is between COLUMNS_HTML_HEAD string and COLUMNS_HTML_TAIL string
COLUMNS_HTML_HEAD = 'var columns'
COLUMNS_HTML_TAIL = ';'

# Country data is COUNTRY_BLOCK_SIZE block size and between COUNTRY_HTML_STARTING_CODE string and
# COUNTRY_HTML_ENDING_CODE
# The countries block ends at COUNTRY_HTML_ENDING_INDEX
COUNTRY_HTML_STARTING_CODE = "<a class=\"mt_a\" href=\"country"
COUNTRY_HTML_ENDING_CODE = "<td style=\"display:none\" data-continent"
COUNTRY_BLOCK_SIZE = 1024
COUNTRY_HTML_ENDING_INDEX = 393000

# The worldwide cases start at WORLDWIDE_CASES_HTML string
WORLDWIDE_CASES_HTML = "Coronavirus Cases:</h1>\n<div class=\"maincounter-number\">""\n<span style=\"color:#aaa\">"

# Update time list - fetch data at the time items in the list
UPDATE_TIME = ['08:00:00', '16:00:00', '00:00:00']

# Error message printed when failing to fetch data
ERR_MSG_FETCH = 'Failed to fetch data. Check HTML code'

# Error messages printed when failing to open a file and writing to a file
ERR_FILE_OPEN = 'Failed to open a file!'
ERR_FILE_WRITE = 'Failed to write to a file!'
