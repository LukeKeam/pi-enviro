# https://www.sqlitetutorial.net/sqlite-python/
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create or make db then connect to a
    a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_tables():
    database = r"data.db"
    sql_create_user_table = """ CREATE TABLE IF NOT EXISTS user  (
                                        id integer PRIMARY KEY,
                                        username text NOT NULL,
                                        token text,
                                        ip_address text
                                    ); """

    # temperature,pressure,humidity,light,oxidised,reduced,nh3,pm1,pm25,pm10
    sql_create_enviro_table = """CREATE TABLE IF NOT EXISTS enviro (
                                    id integer PRIMARY KEY,
                                    datetime text NOT NULL,
                                    temperature integer ,
                                    pressure integer ,
                                    humidity integer,
                                    light integer,
                                    oxidised integer,
                                    reduced integer,
                                    nh3 integer,
                                    pm1 integer,
                                    pm25 integer,
                                    pm10 integer
                                ); """

    """
    user integer NOT NULL,,
    FOREIGN KEY (user) REFERENCES user (id)
    """
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create table
        create_table(conn, sql_create_user_table)
        # create enviro table
        create_table(conn, sql_create_enviro_table)
    else:
        print("Error! cannot create the database connection.")


###################################################################
# insert data into user
###################################################################
def create_username(conn, data):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO user(username,token,ip_address)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid


###################################################################
# insert data into enviro
###################################################################
def create_enviro(conn, enviro_data):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """
    sql = ''' INSERT INTO enviro(datetime,temperature,pressure,humidity,light,oxidised,reduced,nh3,pm1,pm25,pm10)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, enviro_data)
    conn.commit()
    return cur.lastrowid


###################################################################
# insert data into all
###################################################################
def add_data():
    database = r"data.db"
    # create a database connection
    conn = create_connection(database)
    i = 1
    while i != 2:
        with conn:
            # insert user data
            user_data = ('username', 'token', 'ip_address')
            create_username(conn, user_data)
            # insert database
            # datetime,temperature,pressure,humidity,light,oxidised,reduced,nh3,pm1,pm25,pm10
            enviro_data = ('2000-01-01 01:02:02.001', '20', '1000', '59', '9', '1', '1', '1', '1', '1', '1', '1')
            create_enviro(conn, enviro_data)
            #
            print('i', i)
            if i >= 2:
                break
            i = i + 1

if __name__ == '__main__':
    create_tables()
    add_data()

