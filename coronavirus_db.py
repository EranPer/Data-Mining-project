import pymysql


def create_db(host, user, passwd, db='corona'):
    """
    provides a basic access to a Connection with the mysql server and to a specific
    database if exist, and if not, creates it.
    :param host: your mysql host name.
    :param user: your mysql user.
    :param passwd: your mysql password.
    :param db: name of database.
    :return: True / False if the creation of DB succeeded.
    """
    conn = pymysql.connect(host, user, passwd)
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")

    for database in cursor:
        if database[0] == db:
            return False

    cursor.execute(f'create database {db}')
    return True


def create_connection(host, user, passwd, db='corona'):
    """
    connects to an existing/ newly existing mysql database with the engine created
    in create_engine function
    :param host: your mysql host name.
    :param user: your mysql user.
    :param passwd: your mysql password.
    :param db: name of database.
    :return: connection to a database.
    """
    db = pymysql.connect(host, user, passwd, db)
    return db


def create_table(db, table_name):

    cursor = db.cursor()

    cursor.execute("SHOW TABLES")

    for table in cursor:
        print(table[0])
        if table[0] == table_name:
            return False

    if table_name == 'countries':
        sql = """CREATE TABLE """

        sql += table_name
        sql += """(id CHAR(20) NOT NULL PRIMARY KEY,
                    name CHAR(20),
                    total_deaths INT,  
                    total_recovered INT,
                    critical_cases INT,
                    total_tests INT )"""

        cursor.execute(sql)

    elif table_name == 'history':
        sql = """CREATE TABLE """

        sql += table_name
        sql += """(id INT NOT NULL PRIMARY KEY,
                    country_Id CHAR(20),
                    date INT,  
                    active_cases INT,
                    daily_deaths INT )"""

    elif table_name == 'states':
        sql = """CREATE TABLE """

        sql += table_name
        sql += """(id CHAR(20) NOT NULL PRIMARY KEY,
                        name CHAR(20),
                        total_deaths INT,  
                        total_recovered INT,
                        critical_cases INT,
                        total_tests INT )"""

        cursor.execute(sql)

    return True

