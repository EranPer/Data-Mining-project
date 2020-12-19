from coronavirus import Coronavirus
from API_data_parsing import *
from creating_db_scraper_api import *
from config import *
from datetime import datetime
import argparse
import time
import sys
import logging


def set_logger(log_name='logger.log', level=logging.INFO):
    """
    This function creates a logger, by using the logging package, for printing to a log file and to screen.
    :param log_name: The name of the log file. 'logger.log' is the default name.
    :param level: The level of logging. logging.INFO is the default level.
    :return: The logger
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    # Create Formatter
    formatter = logging.Formatter(
        '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

    # create a file handler and add it to logger
    file_handler = logging.FileHandler(log_name)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


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


def get_parser():
    """
    This function set arguments for the parser from the argparse package.
    :return: a parser.
    """
    parser = argparse.ArgumentParser(description='Data Mining Project.')
    parser.add_argument('--times', metavar='times.txt', type=str,
                        help='A file containing update times in the format 00:00:00.')
    parser.add_argument('--countries', metavar='countries.txt', type=str,
                        help='A file containing names of countries.')
    parser.add_argument('--table', choices=['world', 'countries', 'history', 'api', 'all'],
                        default='all', help='table choice for scraping (default: all)')
    return parser


def handle_args(args):
    """
    This function handles all the arguments from parser
    :param args:
    :return:
    """
    if vars(args)['times'] is None:
        update_times_list = UPDATE_TIME
    else:
        update_times_list = get_update_times_list(vars(args)['times'])

    if vars(args)['countries'] is None:
        countries_fetch_list = COUNTRIES_FETCH
    else:
        countries_fetch_list = get_countries_list(vars(args)['countries'])

    table = vars(args)['table']

    return update_times_list, countries_fetch_list, table


def set_connection_mysql(user, pwd, host):
    """
    This function creates an engine and connects to MySQL with username, password and host.
    :param user: the user name.
    :param pwd: the password.
    :param host: the host (local or remote).
    :return: the engine and the connection.
    """
    engine = make_engine(USER_NAME, PASSWORD, HOST)
    connection = create_connection(engine)
    return connection, engine


def create_tables(engine):
    """
    This function create or use the tables in the database
    :param engine: the engine.
    :return: countries and history tables and a boolean variables if they were created (true) or not.
    """
    countries, table_countries_created = create_or_use(engine, 'countries')
    history, table_history_created = create_or_use(engine, 'history')
    return countries, table_countries_created, history, table_history_created


def main():
    """
    The main function. Get user input: Update times and a file containing countries.
    Fetches data at start and every time on the 'update_times' list.
    :return:
    """
    # Create logger file
    logger = set_logger('coronavirus.log')

    # Parse arguments
    parser = get_parser()
    args = parser.parse_args()

    # create lists from files - times and countries
    update_times_list, countries_fetch_list, table = handle_args(args)
    logger.info(f'times={update_times_list}. countries={countries_fetch_list}')

    # Create a coronavirues instance
    cv = Coronavirus(URL, logger)
    logger.info(f'Created Coronavirus object')

    # Create engine and connect to a MySQL server
    connection, engine = set_connection_mysql(USER_NAME, PASSWORD, HOST)
    logger.info(f'Connection to MySQL was established')

    # Create or use countries and history tables in the MySQL server
    countries, table_countries_created, history, table_history_created = create_tables(engine)
    if table_countries_created:
        logger.info(f'countries table was created')
    if table_history_created:
        logger.info(f'history table was created')

    # A loop that parse the data for the first time and every update time
    data_fetched = False
    while True:
        # Check for update time if it's time to refresh data or if the code is running for the first time
        if refresh_data(update_times_list) or not data_fetched:

            # Starting fetching data with the web scraper
            logger.info(f'Started web scraping')
            cv.web_scraper(table, countries_fetch_list)
            data_fetched = True
            logger.info(f'Finished web scraping')

            # Starting fetching API data with api query
            if table == 'all' or table == 'api':
                transmission = api_query()
                logger.info(f'Started API query')
                print(transmission)
                logger.info(f'Finished API query')

            # inserting into database
            logger.info(f'Inserting countries info into table...')
            if table_countries_created:
                inserting_country_info(cv.get_countries(), countries, connection, transmission)
                logger.info(f'countries table was created')
            else:
                # updating database countries:
                for country_dict in cv.get_countries():
                    country, update_data, country_code = cv.country_update(country_dict)
                    update_country_info(countries, country_code, update_data, connection)
                logger.info(f'countries table was updated')

            # insert to history
            if not table_history_created:
                for country in countries_fetch_list:
                    # Update country's history into database
                    history_update(country, history, cv.get_history()[country],
                                        connection, engine, countries)
            else:
                # Insert country's history for the first time into database
                logger.info(f'Inserting history data for the fetched countries into history table...')
                inserting_history_info(cv.get_history(), history, connection, engine, countries)
                logger.info(f'countries history was inserted into history table')

            print('Next update/s will occur at:', update_times_list)

        # interval of 1 second
        time.sleep(1)


if __name__ == '__main__':
    main()
