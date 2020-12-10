from coronavirus import Coronavirus
from coronavirus_db import *
from config import *
from datetime import datetime
import time
import sys
import logging


def create_database_and_tables():
    """
    This function creates database and tables for the data.
    :return:
    """
    create_db(HOST, USER_NAME, PASSWORD)

    db = create_connection(HOST, USER_NAME, PASSWORD)
    create_table(db, 'countries')
    create_table(db, 'history')
    create_table(db, 'countries')


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


def main():
    """
    The main function. Get user input: Update times and a file containing countries.
    Fetches data at start and every time on the 'update_times' list.
    :return:
    """
    logger = set_logger('coronavirus.log')

    create_database_and_tables()

    cv = Coronavirus(URL, logger)

    if len(sys.argv) != REQUIRED_NUM_OF_ARGS:
        print("usage: ./coronavirus_2.0.py times.txt countries.txt")
        logger.info(f'Number of arguments: {len(sys.argv)}. Taking default args instead')
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
        logger.info(f'Files were found. times={update_times_list}. countries={countries_fetch_list}')

    data_fetched = False
    while True:
        # Check for update time if it's time to refresh data or if the code is running for the first time
        if refresh_data(update_times_list) or not data_fetched:
            logger.info(f'Started web scraping')

            cv.parsing_data(countries_fetch_list)
            data_fetched = True

            logger.info(f'Finished web scraping')

            print('Next update/s will occur at:', update_times_list)

        # interval of 1 second
        time.sleep(1)


if __name__ == '__main__':
    main()
