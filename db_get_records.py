# https://www.sqlitetutorial.net/sqlite-python/
import time
from db_connect import db_create_connection

# db connect
database = r"data.db"
db_file = database
conn = db_create_connection(db_file)

# check db
def db_select_all(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
cur = conn.cursor()


print('enviro')
date_time_from_server = "20200827091549.000"
cur.execute("SELECT * FROM enviro ORDER BY id DESC LIMIT 500")  # " WHERE datetime > {0} ".format(
# date_time_from_server))
rows = cur.fetchall()
for row in rows:
    time.sleep(.02)
    print(row)


print('')
print('users')
cur.execute("SELECT * FROM user")
rows = cur.fetchall()
for row in rows:
    time.sleep(.1)
    print(row)

