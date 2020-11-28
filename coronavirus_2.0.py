import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys
from config import *


def html(url):
    """
    Function html
    Receives a url address and returns its html code.
    :param url: the url to parse.
    :return: html page code.
    """
    page = requests.get(url)
    txt = page.text
    return txt


def parsing_columns_data(starting_line, ending_line, text, number_of_columns=14):
    """
    Function parsing_columns_data
    Searching in a html code for columns data (table headers).
    :param starting_line: starting string of the columns html block.
    :param ending_line: ending string of the columns html block.
    :param text: string of full or partial html code to search in
    :return: a list of the columns values.
    """
    columns = ['Country']
    starting_index_of_columns = text.find(starting_line)
    ending_index_of_columns = text[starting_index_of_columns:].find(ending_line)
    code = text[starting_index_of_columns:starting_index_of_columns + ending_index_of_columns]
    for i in range(number_of_columns - 1):
        starting_index_of_columns = code.find('\'')
        ending_index_of_columns = code[starting_index_of_columns + 1:].find('\'')
        value = code[starting_index_of_columns + 1:starting_index_of_columns + ending_index_of_columns + 1]
        code = code[starting_index_of_columns + ending_index_of_columns + 2:]
        columns.append(value)
    return columns


def parsing_country_values(row_list, list_block):
    """
    This function helps to retrieve the values from countries line by line in a block of code.
    :param row_list: the list to append the values for each country.
    :param list_block: the html code block.
    :return: row_list: the list with the values of countries.
    """
    for line in list_block[:-1]:
        value_starting_index = line.find('>')
        value_ending_index = line[value_starting_index:].find('<')
        if value_starting_index == -1 or value_ending_index == -1:
            continue
        value = line[value_starting_index + 1:value_starting_index + value_ending_index]
        if value == '':
            value_starting_index = line.find('>') + 1
            value_starting_index = line.find('>', value_starting_index)
            value_ending_index = line[value_starting_index:].find('<')
            value = line[value_starting_index + 1:value_starting_index + value_ending_index]
        row_list.append(value)
    return row_list


def cleaning_countries_values(row_list):
    """
    This function helps to clean the data for each country - replace 'N/A' or blank values with 'None'
    and to convert the numerical value to float.
    :param row_list: the list with values to check and clean.
    :return: row_list: the list with the float or None values only.
    """
    for i, number in enumerate(row_list[1:]):
        if number.strip() == '' or number == 'N/A':
            row_list[i + 1] = None
        elif number.find('.') == -1:
            row_list[i + 1] = int(number.replace(',', ''))
        else:
            row_list[i + 1] = float(number)
    return row_list


def parsing_country_data(starting_line, ending_line, text, countries_fetch_list, countries_set, country_link_dict):
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

    row_list = parsing_country_values(row_list, list_block)
    row_list = cleaning_countries_values(row_list)

    country = row_list[0]
    if len(countries_fetch_list) > 0:
        if country not in countries_fetch_list:
            return []

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


def countries_to_list(countries_fetch_list, country_list, txt, country_set, country_link_dict):
    """
    This function helps to fetch the countries data in a text and add into a list of countries.
    :param countries_fetch_list: the list of country to fetch from.
    :param country_list: the country list to append the new country values.
    :param txt: the HTML code.
    :param country_set: the set of countries, will be updated if need in case of new countries.
    :param country_link_dict: the dictionary of each country with the link to its webpage.
    :return: the updated list.
    """
    starting_index = txt.find(COUNTRY_HTML_STARTING_CODE)
    ending_index = COUNTRY_HTML_ENDING_INDEX
    for i in range(starting_index, ending_index, COUNTRY_BLOCK_SIZE):
        country_list.append(parsing_country_data(COUNTRY_HTML_STARTING_CODE,
                                                 COUNTRY_HTML_ENDING_CODE, txt[i:],
                                                 countries_fetch_list,
                                                 country_set, country_link_dict))

    country_list = [x for x in country_list if x != []]
    return country_list


def cell_numeric_value(cell):
    """
     good for both below functions
     NEED TO FINISH THE DOCUMENTATION
    :param cell:
    :return:
    """
    cell_final = cell.text.strip()
    if '+' in cell:
        cell_final = int(cell_final[1:].replace(',', ''))
    elif cell_final == '' or cell_final == 'N/A' or cell_final == None:
        cell_final = -1    ## instead of None (for database insertion sake)
    else:
        # print(cell_final, type(cell_final))
        cell_final = round(float(cell_final.replace(',', '')))
    return cell_final


def parsing_state_page(txt_page):
    """
    still not documented - that function thkes the usa url and parses the states data
    :param txt_page:
    :return:
    """
    soup = BeautifulSoup(txt_page, features="lxml")
    table = soup.select('#usa_table_countries_today')[0]

    table_list = []

    for table_row in table.findAll('tr'):  # tr = table row in html
        cells = table_row.findAll('td')  # td = table column in html
        if len(cells) > 0:
            country_name = cells[1].text.strip()
            # I want to ignore the 'total' row
            if 'Total' in country_name or 'World' in country_name:
                continue

            table_dictionaries = {
                'state': country_name,
                'total cases': cell_numeric_value(cells[2]),
                'new cases': cell_numeric_value(cells[3]),
                'total death': cell_numeric_value(cells[4]),
                'new deaths': cell_numeric_value(cells[5]),
                'total recovered': cell_numeric_value(cells[6]),
                'active cases': cell_numeric_value(cells[7]),
                'cases per 1 million': cell_numeric_value(cells[8]),
                'deaths per 1 million': cell_numeric_value(cells[9]),
                'total tests': cell_numeric_value(cells[10]),
                'test  per1 million': cell_numeric_value(cells[11]),
                'population': cell_numeric_value(cells[12])
            }
            table_list.append(table_dictionaries)

    return table_list


def parsing_country_page(txt_page):
    """
     !!! ERAN !!!
     this function is good and running!
    :param txt_page:
    :return:
    """
    soup = BeautifulSoup(txt_page, features="lxml")
    table = soup.select('#main_table_countries_today')[0]

    table_list = []

    for table_row in table.findAll('tr'):  # tr = table row in html
        cells = table_row.findAll('td')  # td = table column in html

        if len(cells) > 0:
            country_name = cells[1].text.strip()
            if 'Total' in country_name or 'World' in country_name:
                continue

            table_dictionaries = {
                'country': country_name,
                'total cases': cell_numeric_value(cells[2]),
                'new cases': cell_numeric_value(cells[3]),
                'total death': cell_numeric_value(cells[4]),
                'new deaths': cell_numeric_value(cells[5]),
                'total recovered': cell_numeric_value(cells[6]),
                'active cases': cell_numeric_value(cells[8]),
                'critical cases': cell_numeric_value(cells[9]),
                'cases per 1 million': cell_numeric_value(cells[10]),
                'deaths per 1 million': cell_numeric_value(cells[11]),
                'total tests': cell_numeric_value(cells[12]),
                'test per1 million': cell_numeric_value(cells[13]),
                'population': cell_numeric_value(cells[14])
            }
            table_list.append(table_dictionaries)

    return table_list


def parsing_data(countries_fetch_list):
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

    try:
        print(parsing_main_data(txt))
        print()

        columns_list = parsing_columns_data(COLUMNS_HTML_HEAD, COLUMNS_HTML_TAIL, txt)
        country_list.append(columns_list)
        country_list = countries_to_list(countries_fetch_list, country_list, txt, country_set, country_link_dict)

        for country in country_list:
            print(country)
        print('\ncountries:', country_set)
        print('number of countries:', len(country_set), '\n')

        for country in country_set:
            txt = html(URL + 'country/' + country_link_dict[country] + '/')
            country_history[country] = parsing_country_history(txt)
            print(country)
            print(country_history[country])

        usa_states = parsing_state_page(html(USA_URL))
        for state in usa_states:
            print(state)
        print(f'number of USA states and sub-regions: {len(usa_states)}')

    except Exception as ex:
        print(ex, ERR_MSG_FETCH)
        sys.exit(1)
    return True


def get_update_times_list(filename):
    """
    This function receives a file containing update times and returns a list of those times.
    :param filename: a file containing update times in the format 00:00:00 in every line.
    :return: a list of the update times.
    """
    update_times_list = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.replace('\n', '')
            update_times_list.append(line)
    return update_times_list


def get_countries_list(filename):
    """
    This function receives a file containing countries and returns a list of those countries.
    :param filename: a file containing names of countries in every line.
    :return: a list of the countries.
    """
    countries_list = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.replace('\n', '')
            countries_list.append(line)
    return countries_list


def main():
    """
    The main function. Get user input: Update times and a file containing countries.
    Fetches data at start and every time on the 'update_times' list.
    :return:
    """
    if len(sys.argv) != REQUIRED_NUM_OF_ARGS:
        print("usage: ./coronavirus_2.0.py times.txt countries.txt")
        print("Taking default instead")
        update_times_list = UPDATE_TIME
        countries_fetch_list = COUNTRIES_FETCH
        if not countries_fetch_list:
            stat = 'all'
        else:
            stat = countries_fetch_list
        print('times=' + str(update_times_list) + ' countries=' + str(stat) + '\n')
    else:
        update_times_list = get_update_times_list(sys.argv[ARG_UPDATES_FILE])
        countries_fetch_list = get_countries_list(sys.argv[ARG_COUNTRIES_FILE])
        print('times=' + str(update_times_list) + ' countries=' + str(countries_fetch_list) + '\n')

    data_fetched = False
    while True:
        # Check for update time if it's time to refresh data or if the code is running for the first time
        if refresh_data(update_times_list) or not data_fetched:
            current_time = datetime.now().strftime("%H:%M:%S")
            print("Starting fetching data at:", current_time)

            parsing_data(countries_fetch_list)
            data_fetched = True

            current_time = datetime.now().strftime("%H:%M:%S")
            print("Done fetching data at:", current_time)
            print('Next update/s will occur at:', update_times_list)

        # interval of 1 second
        time.sleep(1)


if __name__ == '__main__':
    main()

