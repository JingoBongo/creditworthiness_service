import sqlite3
from binascii import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn



def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Business_Services")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def main():
    database = r"D:\files\yearV\cloud\reditworthiness_service\resources\main_db2.db"

    # create a database connection
    conn = create_connection(database)
    print('here')
    with conn:
        print("2. Query all tasks")
        select_all_tasks(conn)



if __name__ == '__main__':
    # main()
    a = print('sdfsdf')