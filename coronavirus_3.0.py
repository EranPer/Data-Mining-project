from datetime import datetime
import argparse
import requests
from bs4 import BeautifulSoup
import time
import sys
from config import *
from API_parser import *
from creating_db_scraper_api import *



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
    :return: a dictionary of 6 key cases: name and 5 graphs info. each graph  in a key and it value
    is another dictionary, which had 2 key-value pair, containing list of dates and list of number of instances
    """
    starting_index = 0
    country_history = {}
    graph_list = ['Total Cases', 'Daily New Cases', 'Active Cases', 'Total Deaths', 'Daily Deaths']

    for graph in graph_list:

        if txt.find(graph) == -1:
            country_history[graph] = dict()
            continue

        starting_index = starting_index + txt[starting_index:].find(graph)

        starting_index = starting_index + txt[starting_index:].find('categories: [')
        ending_index = starting_index + txt[starting_index:].find(']')
        categories_list = txt[starting_index + len('categories: [') + 1:ending_index - 1].split('\",\"')
        if len(categories_list) < 1:
            categories_list = []

        starting_index = starting_index + txt[starting_index:].find('data: [')
        ending_index = starting_index + txt[starting_index:].find(']')
        data_list = txt[starting_index + len('data: ['):ending_index].split(',')
        if len(data_list) < 1:
            data_list = []

        country_history[graph] = {'dates': categories_list, 'instances': data_list}

    return country_history


def get_countries_links(txt):
    """
    This function gets an html code and returns a dictionary with countries as keys and URL links as values.
    :param txt: the html code (string) of the country's webpage.
    :return: a dictionary with a URL link for each country to its webpage.
    """
    country_link_dict = {}

    soup = BeautifulSoup(txt, features="lxml")

    table = soup.select('#main_table_countries_today')[0]
    for link in table.find_all('a'):
        if 'country' in str(link):
            country = link.get_text(strip=True)
            country_link = link.get('href')
            country_link_dict[country] = country_link
    return country_link_dict


def cell_numeric_value(cell):
    """
     this helper function of parsing_country_page function
     it helps to edit the values of each dictionary key.
    :return:
    """
    cell_final = cell.text.strip()
    if '+' in cell:
        cell_final = int(cell_final[1:].replace(',', ''))
    elif cell_final == '' or cell_final == 'N/A' or cell_final is None:
        cell_final = -1  ## instead of None (for database insertion sake)
    else:
        # print(cell_final, type(cell_final))
        cell_final = round(float(cell_final.replace(',', '')))
    return cell_final


def parsing_country_page(txt_page):
    """
    Searching in the html code for country's relevant data regarding the Coronavirus cases
    and returning its values in a list of dictionaries, where each dictionary represent a different country.
    :param txt_page: the HTML code.
    :return: list of countries dictionaries
    """
    soup = BeautifulSoup(txt_page, features="lxml")
    table = soup.select('#main_table_countries_today')[0]

    table_list = []

    for table_row in table.findAll('tr'):  # tr = table row in html
        cells = table_row.findAll('td')  # td = table column in html

        if len(cells) > 0:
            country_name = cells[1].text.strip()
            if country_name in ['Total:', 'World', 'North America',
                                'Asia', 'South America', 'Europe', 'Africa', 'Oceania', '']:
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
    country_history = {}
    engine = make_engine(USER, PASSWORD, HOST)
    connection = create_connection(engine)
    countries = create_or_use(engine, 'countries')
    history = create_or_use(engine, 'history')
    # print(query_db(engine, connection, countries, where="USA"))

    # global corona info:
    print(parsing_main_data(txt))

    # each country corona info
    all_countries = parsing_country_page(txt)
    for country_dict in all_countries:
        print(country_dict)
        # updating database countries:
        if country_dict['country'] in COUNTRIES_NAMES_TO_CODES.keys():
            country_code = COUNTRIES_NAMES_TO_CODES[country_dict['country']]
            update_data = {'total_cases': country_dict['total cases'],
                           'new_cases': country_dict['new cases'],
                           'total_deaths': country_dict['total death'],
                           'new_deaths': country_dict['new deaths'],
                           'total_recovered': country_dict['total recovered'],
                           'active_cases': country_dict['active cases'],
                           'critical_cases': country_dict['critical cases'],
                           'cases_per_1m': country_dict['cases per 1 million'],
                           'deaths_per_1m': country_dict['deaths per 1 million'],
                           'total_tests': country_dict['total tests'],
                           'tests_per_1m': country_dict['test per1 million'],
                           'population': country_dict['population']}
            update_country_info(countries, country_code, update_data, connection)
    # # inserting to database
    # inserting_country_info(all_countries, countries, connection)  # first time insert function

    # countries list and number
    country_list = [country_dict['country'] for country_dict in all_countries]
    print('\ncountries:', country_list)
    print('number of countries:', len(country_list), '\n')

    # country history (from graphs):
    country_link_dict = get_countries_links(txt)
    if not countries_fetch_list:
        countries_fetch_list = country_list

    not_in = []
    for country in countries_fetch_list:
        if country not in COUNTRIES_NAMES_TO_CODES.keys():
            if country not in COUNTRIES_NAMES_TO_CODES.values():
                not_in.append(country)

    for country in countries_fetch_list:
        if country not in not_in:
            txt = html(URL + country_link_dict[country] + '/')
            country_history[country] = parsing_country_history(txt)
            # # history to database:
            # update the history table in database
            if country in COUNTRIES_NAMES_TO_CODES.keys():
                country_code = COUNTRIES_NAMES_TO_CODES[country]
                if 'dates' in country_history[country].keys():
                    for date in country_history[country]['dates']:
                        add_new_history_info(history, country_code, country_history[country],
                                             date, connection, engine, countries)
    # inserting_history_info(country_history, history, connection, engine, countries)  # first time insert function

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
