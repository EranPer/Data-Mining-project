from bs4 import BeautifulSoup
from config import *
import requests


class Coronavirus:
    """
    Class Coronavirus. Initiate a coronavirus object with a url and a logger file.
    """
    def __init__(self, url, logger):
        self.url = url
        self.logger = logger
        self.world = {}
        self.countries = []
        self.history = {}

    def get_global(self):
        """
        :return: global data
        """
        return self.world

    def get_countries(self):
        """
        :return: countries data
        """
        return self.countries

    def get_history(self):
        """
        :return: history data
        """
        return self.history

    def html(self, url):
        """
        Function html
        Receives a url address and returns its html code.
        :param url: the url to parse.
        :return: html page code.
        """
        page = requests.get(url)
        txt = page.text
        self.logger.info(f'{url} was successfully parsed')
        return txt

    def parsing_main_data(self, txt):
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

    def parsing_country_history(self, txt):
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

            starting_index = starting_index + txt[starting_index:].find('data: [')
            ending_index = starting_index + txt[starting_index:].find(']')
            data_list = txt[starting_index + len('data: ['):ending_index].split(',')

            country_history[graph] = {'dates': categories_list, 'instances': data_list}

        return country_history

    def get_countries_links(self, txt):
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

    def cell_numeric_value(self, cell):
        """
         this helper function of parsing_country_page function
         it helps to edit the values of each dictionary key.
        :return:
        """
        cell_final = cell.text.strip()
        if '+' in cell:
            cell_final = int(cell_final[1:].replace(',', ''))
        elif cell_final == '' or cell_final == 'N/A' or cell_final is None:
            cell_final = -1    ## insteaCoronavirusd of None (for database insertion sake)
        else:
            # print(cell_final, type(cell_final))
            cell_final = round(float(cell_final.replace(',', '')))
        return cell_final

    def parsing_country_page(self, txt_page):
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
                    'total cases': self.cell_numeric_value(cells[2]),
                    'new cases': self.cell_numeric_value(cells[3]),
                    'total death': self.cell_numeric_value(cells[4]),
                    'new deaths': self.cell_numeric_value(cells[5]),
                    'total recovered': self.cell_numeric_value(cells[6]),
                    'active cases': self.cell_numeric_value(cells[8]),
                    'critical cases': self.cell_numeric_value(cells[9]),
                    'cases per 1 million': self.cell_numeric_value(cells[10]),
                    'deaths per 1 million': self.cell_numeric_value(cells[11]),
                    'total tests': self.cell_numeric_value(cells[12]),
                    'test per1 million': self.cell_numeric_value(cells[13]),
                    'population': self.cell_numeric_value(cells[14])
                }
                table_list.append(table_dictionaries)

        return table_list

    @staticmethod
    def country_update(country_dict):
        if country_dict['country'] in COUNTRIES_NAMES_TO_CODES.keys():
            country = country_dict['country']
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

            return country, update_data, country_code
        return None, None, None

    def web_scraper(self, table, countries_fetch_list):
        """
        Function parsing_data
        Parsing data of Corona virus cases from the given website.
        :return: True or False if data fetching succeeded or not.
        """
        txt = self.html(self.url)
        country_history = {}

        try:
            # Fetching global data and printing to console
            if table == 'all' or table == 'world':
                # global corona info:
                self.world = self.parsing_main_data(txt)
                print(self.world)

            # Fetching countries data
            if table == 'all' or table == 'countries':
                self.countries = self.parsing_country_page(txt)

                # Printing countries data to console
                for country_dict in self.countries:
                    # each country corona info
                    print(country_dict)

                # the list of countries
                country_list = [country_dict['country'] for country_dict in self.countries]
                print(len(country_list), 'countries:', country_list)

            if table == 'all' or table == 'history':
                # get link for each country webpage:
                country_link_dict = self.get_countries_links(txt)
                if not countries_fetch_list:
                    countries_fetch_list = country_list

                # for each country fetch its history
                for country in countries_fetch_list:
                    if country in COUNTRIES_NAMES_TO_CODES.keys():
                        txt = self.html(self.url + country_link_dict[country])
                        country_history[country] = self.parsing_country_history(txt)
                        print(f'{country}\n{country_history[country]}')
                self.history = country_history

        except Exception as ex:
            self.logger.error(f'{ERR_MSG_FETCH}')
            raise ValueError(ERR_MSG_FETCH)
        return True


