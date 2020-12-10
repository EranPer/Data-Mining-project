from coronavirus import Coronavirus
from API_data_parsing import *
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


def main():
    """
    The main function. Get user input: Update times and a file containing countries.
    Fetches data at start and every time on the 'update_times' list.
    :return:
    """
    logger = set_logger('coronavirus.log')

    cv = Coronavirus(URL, logger)

    parser = get_parser()
    args = parser.parse_args()
    update_times_list, countries_fetch_list, table = handle_args(args)
    logger.info(f'times={update_times_list}. countries={countries_fetch_list}')

    data_fetched = False
    while True:
        # Check for update time if it's time to refresh data or if the code is running for the first time
        if refresh_data(update_times_list) or not data_fetched:

            logger.info(f'Started web scraping')
            cv.parsing_data(table, countries_fetch_list)
            data_fetched = True
            logger.info(f'Finished web scraping')

            if table == 'all' or table == 'api':
                logger.info(f'Started API query')
                print(api_query())
                logger.info(f'Finished API query')

            print('Next update/s will occur at:', update_times_list)

        # interval of 1 second
        time.sleep(1)


if __name__ == '__main__':
    main()
