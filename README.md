![Build Status](https://www.itc.tech/wp-content/uploads/2018/03/site-logo.png)

# Data Mining Project - Coronavirus Cases Web Scraper
This python code uses the Coronavirus website https://www.worldometers.info/coronavirus/ to fetch data about the virus. The data is both globally and individually for each country , and its history, of coronavirus cases. The code fetchs the data when running it first, and updates it every x time.

## Team Members
[Eran Perelman](https://github.com/EranPer/ "Eran Perelman's GitHub")<br/>
[Nofar Herman](https://github.com/nofr "Nofar Herman's GitHub")<br/>

## Process explanation

### Checkpoint 1
- We used requests, beautifulsoup and lxml platforms for creating functions of data parsing. The data is stored in lists, sets and dictionaries. The parsing code runs in a loop that updates the data every interval of time. The user can change the update times by changing it in the constant list in the config file.

### Checkpoint 2
- Command line interface - added web scraper options to be able to call it with different arguments from the terminal. Now you can use update times and countries arguments: 1st argument is a file containing update times to update data (every line in the format 00:00:00) and 2nd file containing countries, in every line. The code will fetch only relevant country's history, mentioned in the ```python countries``` file, and will update it any given time, mentioned in the update_times file.

## Installation
You should install python with basic installations, such as DateTime, and all the prerequisites in the requirements.txt file.
```bash
pip install -r requirements.txt
```

## How to use the code
The program fetches the data at first and update it in any given time.
After installation, upload the python file to your favorite Python editor and run the code. 
Alternatively, run the code from the CLI (i.e. CMD in windows). The usage is the following:
```bash
Usage: coronavirus_2.0.py update_times.txt countries.txt
```

## DISCLAIMER
We use this information of the Coronavirus cases from the worldometers website for learning purposes only!
<br />All rights reserved ©
<br /><br />[Click for more details](https://www.shorturl.at/bqACD "The motivation")
