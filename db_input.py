from db_connect import db_create_connection

def db_send_to_local_db(datetime,temperature,pressure,humidity,light,oxidised,reduced,nh3,pm1,pm25,pm10, decibels):
    """
    store only 6min intervals while moving
    if vehicle move stop then store that
        and wait till move start to start again
    """
    def create_task(conn, task):
        """
        Create a new task
        :param conn:
        :param task:
        :return:
        """
        sql = ''' INSERT INTO enviro(datetime,temperature,pressure,humidity,light,oxidised,reduced,nh3,pm1,pm25,pm10,decibels)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid
    database = r"data.db"
    # create a database connection
    conn = db_create_connection(database)
    with conn:
        """
        id integer PRIMARY KEY,
        datetime text NOT NULL,
        longitude integer NOT NULL,
        latitude integer NOT NULL,
        speed integer,
        vehicle_move_stop integer,
        vehicle_move_start integer,
        alert integer
        """
        # task_1 = ('20200827091548.000', '-27.701941', '153.215176', '25', '1', '1', '1',)
        # create_task(conn, task_1)
        # create tasks
        task_2 = (datetime, temperature, pressure, humidity, light, oxidised, reduced, nh3, pm1, pm25, pm10, decibels)
        create_task(conn, task_2)

