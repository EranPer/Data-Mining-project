from sqlalchemy import create_engine, MetaData, Table, Column, Date, Integer, String, Float, ForeignKey, \
    update, select, and_, schema
from sqlalchemy.dialects.mysql import insert
from datetime import datetime
from config import COUNTRIES_NAMES_TO_CODES, USER_NAME, PASSWORD, HOST


def create_engine(user_name, pswd, host, port=3306, db='corona'):
    """
    provides a basic access to a Connection with the mysql server and to a specific
     database if exist, and if not, creates it
    :param user_name: mysql user_name
    :param pswd: your mysql password
    :param host: yor mysql host name
    :param port: mysql port. if not given, the defualt is 3306
    :param db:
    :return:
    """
    engine = create_engine(f'mysql+mysqlconnector://{user_name}:{pswd}@{host}:{port}/{db}')
    if not engine.dialect.has_schema(engine, db):
        engine.execute(schema.CreateSchema(db))
    return engine

# engine = create_engine(USER_NAME, PASSWORD, HOST)


def create_connection(engine):
    """
    connects to an existing/ newly existing mysql database with the engine created
    in create_engine function
    :param engine: basic connection to database
    :return: direct connection to the specific schema.
    """
    connection = engine.connect()
    return connection

# connection = create_connection(engine)


def create_or_use(engine, variable_table_name):
    """
    connect and reflect the wanted table inn the database if exist,
    else, create it.
    :param engine: the engine connection
    :param variable_table_name: the name of the desired table
    :return: a direct reflection of the table
    """
    if not engine.dialect.has_table(engine, variable_table_name):  # If table don't exist, Create.
        metadata = MetaData(engine)
        if variable_table_name == 'countries':
            # Create a table with the appropriate Columns
            Table(variable_table_name, metadata,
                  Column('id', String, primary_key=True, index=True, nullable=False, unique=True),
                  Column('name', String), Column('total_cases', Integer), Column('new_cases', Integer),
                  Column('total_deaths', Integer), Column('new_deaths', Integer),
                  Column('total_recovered', Integer), Column('active_cases', Integer),
                  Column('critical_cases', Integer), Column('cases_per_1m', Float), Column('deaths_per_1m', Float),
                  Column('total_tests', Integer), Column('tests_per_1m', Float), Column('population', Integer))
            # Implement the creation
            metadata.create_all()

        elif variable_table_name == 'history':
            # Create a table with the appropriate Columns
            Table(variable_table_name, metadata,
                  Column('id', Integer, primary_key=True, nullable=False),
                  Column('country_Id', String, ForeignKey("countries.id"), nullable=False),
                  Column('date', Date), Column('total_cases_g', Integer), Column('daily_cases_g', Integer),
                  Column('active_cases_g', Integer), Column('total_deaths_g', Integer),
                  Column('daily_deaths', Integer))
            # Implement the creation
            metadata.create_all()

        elif variable_table_name == 'states':
            # Create a table with the appropriate Columns
            Table(variable_table_name, metadata,
                  Column('id', Integer, primary_key=True, nullable=False, unique=True),
                  Column('country_Id', String, ForeignKey("countries.id"), nullable=False),
                  Column('name', String), Column('total_cases', Integer), Column('new_cases', Integer),
                  Column('total_deaths', Integer), Column('new_deaths', Integer),
                  Column('total_recovered', Integer), Column('active_cases', Integer),
                  Column('cases_per_1m', Float), Column('deaths_per_1m', Float),
                  Column('total_tests', Integer), Column('tests_per_1m', Float), Column('population', Integer))
            # Implement the creation
            metadata.create_all()

    # reflect the data in database:
    metadata = MetaData()
    table_name = Table(variable_table_name, metadata, autoload=True, autoload_with=engine)
    return table_name


# countries = create_or_use(engine, 'countries')
# history = create_or_use(engine, 'history')
# states = create_or_use(engine, 'states')

def inserting_country_info(countries_info, countries_table, connection):
    """
    mainly for first usage: to insert the data into the countries table
    :param countries_info: a list of dictionaries, each represents a country, with the following values:
    country_name (string), new cases (int), total deaths (int), new deaths (int), total recovered cases (int),
    active cases (int), crical cases number (int), cases per 1 million population ratio (float),
    deaths per 1 million population ratio (float), number of tests (int),
    tests that were done per 1 million population ratio (float), total population (int)
    :param countries_table: the table name we want to insert the data to (-> the countries table)
    :param connection: the direct connection to the relevant mysql database.
    """
    for i, row in enumerate(countries_info):
        stmt = insert(countries_table).values(id=COUNTRIES_NAMES_TO_CODES[row['country']], name=row['country'],
                                              total_cases=row['total cases'], new_cases=row['new cases'],
                                              total_deaths=row['total death'], new_deaths=row['new deaths'],
                                              total_recovered=row['total recovered'], active_cases=row['active cases'],
                                              critical_cases=row['critical cases'],
                                              cases_per_1m=row['cases per 1 million'],
                                              deaths_per_1m=row['deaths per 1 million'], total_tests=row['total tests'],
                                              tests_per_1m=row['test per1 million'], population=row['population'])
        connection.execute(stmt)


def inserting_history_info(history_info, history_table, connection):
    """
    inserts the data into the history table.
    :param history_info: a nested dictionary which built in the following format:
    {country1_name: {graph1_name: {dates:[], instances:[]},...,graph5_name: {dates:[], instances:[]}}, country1_name:...}
    the graphs names are: 'Total Cases', 'Daily New Cases', 'Active Cases', 'Total Deaths' and 'Daily Deaths'.
    :param history_table: the name of the database history table (--> history)
    :param connection: the direct connection to the relevant mysql database.
    """
    for key, value in history_info.items():
        all_dates = set(history_info[key]['Total Cases']['dates'] + history_info[key]['Daily New Cases']['dates'] +
                        history_info[key]['Active Cases']['dates'] + history_info[key]['Total Deaths']['dates'] +
                        history_info[key]['Daily Deaths']['dates'])

        dates = [datetime.strptime(f'{x} 20', '%b %d %y') for x in all_dates]

        for i in range(len(dates) - 1):
            values = {'date': dates[i], 'country_id': COUNTRIES_NAMES_TO_CODES[key]}

            if (history_info[key]['Total Cases']['instances'][i].isnumeric()):
                values['total_cases_g'] = int(history_info[key]['Total Cases']['instances'][i])

            if (history_info[key]['Daily New Cases']['instances'][i].isnumeric()):
                values['daily_cases_g'] = int(history_info[key]['Daily New Cases']['instances'][i])

            if (history_info[key]['Active Cases']['instances'][i].isnumeric()):
                values['active_cases_g'] = int(history_info[key]['Active Cases']['instances'][i])

            if (history_info[key]['Total Deaths']['instances'][i].isnumeric()):
                values['total_death_g'] = int(history_info[key]['Total Deaths']['instances'][i])

            if (history_info[key]['Daily Deaths']['instances'][i].isnumeric()):
                values['daily_deaths'] = int(history_info[key]['Daily Deaths']['instances'][i])

            stmt = insert(history_table).values(values)
            connection.execute(stmt)


def update_country_info(countries_table, country_code, values_to_update, connection):
    """
    update an excisting value, by explicitly give the specific country_id.
    :param countries_table:
    :param country_code: the country_id (3-letter-based string for a specific country,
    which is a universal convention instead of numeric id).
    :param values_to_update: what are the values we want to see the table.
    :param connection: the direct connection to the relevant mysql database.
    """
    stmt = update(countries_table).where(countries_table.c.id == country_code).values(values_to_update)
    connection.execute(stmt)


# update_country_info(countries, 'SRB',{'new_cases':2}, connection)

def add_new_history_info(history_table, country_code, values_to_add, date, connection):
    """
    when it comes to the history table, data is only added and not updated,
    so in this case, given a specific date and country code where we what to add data.
    if the it is a new data, it will have a new date, so we will call the insert function.
    in case that the date already excist, we will print to the user a message concerning that issue.
    :param history_table: the name of the history table (--> history)
    :param country_code: the country_id (3-letter-based string for a specific country,
    which is a universal convention instead of numeric id).
    :param values_to_add: what are the new values we want to see the table.
    :param date: the date where we want to see the new value
    :param connection: the direct connection to the relevant mysql database.
    """
    stmt = select([history_table]).where((history_table.c.country_id == country_code) &
                                   (history_table.c.date == datetime.strptime(f'{date} 2020', '%b %d %Y')))
    result = connection.execute(stmt).fetchall()
    if len(result) == 0:
        inserting_history_info(values_to_add, history_table, connection)
    else:
        print('that entry is already exist')
