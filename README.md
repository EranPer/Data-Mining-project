# Data Mining project
## Step 1
This python code uses the Coronavirus website https://www.worldometers.info/coronavirus/ to fetch data about the virus. The data is both globally and individually for each country , and its history, of coronavirus cases. The code fetchs the data when running it first, and updates it every x time.

## Process explanation
We used requests, beautifulsoup and lxml platforms for creating functions of data parsing. The data is stored in lists, sets and dictionaries. There is also a function for saving the data on a file. The parsing code runs in a loop that updates the data every x time. The user can change the update times by changing it in the constant list in the beginning of the code.

## Installation
You should install python with basic installations, such as DateTime, and all the prerequisites in the requirements.txt file.
pip install -r requirements.txt

## DISCLAIMER
We use this information of the Coronavirus cases from the worldometers website for learning purposes only!
