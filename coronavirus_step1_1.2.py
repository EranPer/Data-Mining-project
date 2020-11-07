import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

URL = "https://www.worldometers.info/coronavirus/"

COLUMNS_HTML_HEAD = 'var columns'
COLUMNS_HTML_TAIL = ';'
COUNTRY_HTML_STARTING_CODE = "<a class=\"mt_a\" href=\"country"
COUNTRY_HTML_ENDING_CODE = "<td style=\"display:none\" data-continent"
COUNTRY_BLOCK_SIZE = 1024
COUNTRY_HTML_ENDING_INDEX = 393000

WORLDWIDE_CASES_HTML = "Coronavirus Cases:</h1>\n<div class=\"maincounter-number\">""\n<span style=\"color:#aaa\">"

UPDATE_TIME = ['08:00:00', '16:00:00', '00:00:00']


def html(url):
    """
    Function html

    Receives a url address and returns its html code.
    :param url: the url to parse.
    :return: html page code.
    """
    page = requests.get(url)
    # print(page.text)
    txt = page.text
    return txt


def parsing_columns_data(starting_line, ending_line, text):
    """
    Function parsing_columns_data

    Searching in a html code for columns data (table headers).

    :param starting_line: starting string of the columns html block.
    :param ending_line: ending string of the columns html block.
    :param text: string of full or partial html code to search in
    :return: a list of the columns values.
    """
    columns = ['Country']
    index1 = text.find(starting_line)
    index2 = text[index1:].find(ending_line)
    code = text[index1:index1 + index2]
    for i in range(13):
        index1 = code.find('\'')
        index2 = code[index1 + 1:].find('\'')
        value = code[index1 + 1:index1 + index2 + 1]
        code = code[index1 + index2 + 2:]
        columns.append(value)
    return columns


def parsing_country_data(starting_line, ending_line, text, countries_set, country_link_dict):
    """
    Function parsing_country_data

    Searching in the html code for country's relevant data regarding the Coronavirus cases
    and returning its values in a list.

    :param starting_line: starting string of the country html block.
    :param ending_line: ending string of the country html block.
    :param text: string of full or partial html code to search in.
    :return: a list of the country's values.
    """
    row_list = []
    starting_index = text.find(starting_line)
    ending_index = starting_index + len(starting_line) + text[starting_index + len(starting_line) + 1:].find('/')
    country_link = text[starting_index + len(starting_line) + 1:ending_index + 1]
    text_block = text[starting_index:]
    ending_index = text_block.find(ending_line)
    text_block = text_block[:ending_index]
    list_block = text_block.split('\n')
    for line in list_block[:-1]:
        index1 = line.find('>')
        index2 = line[index1:].find('<')
        if index1 == -1 or index2 == -1:
            continue
        value = line[index1 + 1:index1 + index2]
        if value == '':
            index1 = line.find('>') + 1
            index1 = line.find('>', index1)
            index2 = line[index1:].find('<')
            value = line[index1 + 1:index1 + index2]
        row_list.append(value)
    for i, number in enumerate(row_list[1:]):
        if number.strip() == '' or number == 'N/A':
            row_list[i + 1] = None
        elif number.find('.') == -1:
            row_list[i + 1] = int(number.replace(',', ''))
        else:
            row_list[i + 1] = float(number)
    country = row_list[0]
    if country in countries_set:
        return []
    else:
        countries_set.add(country)
        country_link_dict[country] = country_link
    return row_list


def refresh_data(update_time_list):
    """
        Function refresh_data

        This function receives a list of different time strings in the format of %H:%M:%S and returens True/False if
        the current time matches one of the items (time string) in the list.

        :param update_time_list: receives a list of different time strings (%H:%M:%S)
        :return: True or false if the current time is in the list
        """
    current_time = str(datetime.now().strftime("%H:%M:%S"))
    for time_element in update_time_list:
        if time_element == current_time:
            return True
    return False


def parsing_main_data(txt):
    """

    the main_data function attract the main titles data from the url page,
    and returns it in a dictionary. the three main title -
    'Coronavirus Cases', 'Deaths' and 'Recovered'-
    are presented as a dictionary keys
    and the numerical values are presented as the the key values respectively.

    :param txt: the readable textual given data from URL
    :return: the data as a dictionary
    """

    soup = BeautifulSoup(txt, features="lxml")

    titles_list = []
    numbers_list = []

    center_data = soup.select('#maincounter-wrap')

    for data in center_data:
        titles_list.append(data.select('h1')[0].text[:-1])
        numbers_list.append(int(data.select('span')[0].text.replace(',', "")))
    global_info = dict(zip(titles_list, numbers_list))
    return global_info


def parsing_country_history(txt):
    """
    Function parsing_country_history.

    This function receives an html string of a specific country and returns its coronavirus daily history
    to the current day. The history contains 5 cases: Total Cases, Daily New Cases, Active Cases, Total Deaths and
    Daily Deaths. If the country does not have a case or cases of some kind, for example, Total Deaths = 0,
    It will return a blank list of lists for that case.

    :param txt: the html code (string) of the country's webpage.
    :return: a dictionary of 5 key cases containing 2 lists for each case: the list for days
    (usually starting from Feb 15) and a list of cases per day.
    """
    starting_index = 0
    country_history = {}
    graph_list = ['Total Cases', 'Daily New Cases', 'Active Cases', 'Total Deaths', 'Daily Deaths']

    for graph in graph_list:

        if txt.find(graph) == -1:
            country_history[graph] = [[]]
            continue

        starting_index = starting_index + txt[starting_index:].find(graph)

        starting_index = starting_index + txt[starting_index:].find('categories: [')
        ending_index = starting_index + txt[starting_index:].find(']')

        categories_list = txt[starting_index + len('categories: [') + 1:ending_index - 1].split('\",\"')

        starting_index = starting_index + txt[starting_index:].find('data: [')
        ending_index = starting_index + txt[starting_index:].find(']')

        data_list = txt[starting_index + len('data: ['):ending_index].split(',')

        country_history[graph] = [categories_list, data_list]

    return country_history


def parsing_data():
    """
    Function parsing_data

    Parsing data of Corona virus cases from the given website.

    :return: True or False if data fetching succeeded or not.
    """
    txt = html(URL)
    country_list = []
    country_set = set()
    country_link_dict = {}
    country_history = {}

    current_time = datetime.now().strftime("%H:%M:%S")
    print("Starting fetching data at:", current_time)

    try:
        print(parsing_main_data(txt))

        columns_list = parsing_columns_data(COLUMNS_HTML_HEAD, COLUMNS_HTML_TAIL, txt)
        country_list.append(columns_list)

        starting_index = txt.find(COUNTRY_HTML_STARTING_CODE)
        ending_index = COUNTRY_HTML_ENDING_INDEX
        for i in range(starting_index, ending_index, COUNTRY_BLOCK_SIZE):
            country_list.append(
                parsing_country_data(COUNTRY_HTML_STARTING_CODE, COUNTRY_HTML_ENDING_CODE, txt[i:], country_set, country_link_dict))

        country_list = [x for x in country_list if x != []]

        for country in country_list:
            print(country)

        print()
        print('countries:', country_set)
        print('number of countries:', len(country_set))
        print()

        for country in country_set:
            txt = html(URL + 'country/' + country_link_dict[country] + '/')
            country_history[country] = parsing_country_history(txt)
            print(country)
            print(country_history[country])

        current_time = datetime.now().strftime("%H:%M:%S")
        print("Done fetching data at:", current_time)

        print('Next update/s will occur at:', UPDATE_TIME)
    except:
        print('Failed to fetch data. Check HTML code')
        return False

    return True


def saving_data_to_file(filename, starting_time, ending_time, global_info, country_list, country_set, country_history):
    """
    Function saving_data_to_file

    This function saves the data from the Coronavirus web site to a file.

    :param filename: the name and path to a (txt) file
    :param starting_time: the starting time of the parsing process
    :param ending_time: the ending time of the parsing process
    :param global_info: a dictionary containing global data with keys: 'Coronavirus Cases', 'Deaths' and 'Recovered'
    :param country_list: a list of list (table) of every country with its individual data regarding its cases
    :param country_set: a set of the countries (216)
    :param country_history: a dictionary with country key containing a dictionary with 5 keys of cases for each country.
    Each case containing a list of 2 lists:
    1st list contains the dates (of days) and 2nd list contains the values for each day.
    :return: True or False if creating file and writing to it was successful.
    """
    try:
        f = open(filename, "w")
    except:
        print('Failed to open a file!')
        return False
    try:
        f.write("Starting fetching data at:" + starting_time + "\n")
        f.write(str(global_info) + "\n")
        for country in country_list:
            f.write(str(country) + "\n")
        f.write('countries:' + str(country_set) + "\n")
        f.write('number of countries:' + str(len(country_set)) + "\n")
        for country in country_set:
            f.write(str(country) + "\n")
            f.write(str(country_history[country]) + "\n")
        f.write("Done fetching data at:" + ending_time + "\n")
        f.write('Next update/s will occur at:' + str(UPDATE_TIME) + "\n")
    except:
        print('Failed to write to a file!')
        return False
    finally:
        f.close()
    return True


def main():
    data_fetched = False
    while True:
        if refresh_data(UPDATE_TIME) or not data_fetched:
            parsing_data()
            time.sleep(5)
            data_fetched = True
        time.sleep(1)


if __name__ == '__main__':
    main()
