import os
import sqlite3
from binascii import Error

import psutil
import yaml


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
    cur.execute("SELECT * FROM Sys_services")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def main():
    database = r"D:\Files\univYear5\cloud\creditworthiness_service\resources\main_db2.db"

    # create a database connection
    conn = create_connection(database)
    print('here')
    with conn:
        print("2. Query all tasks")
        select_all_tasks(conn)


cur_file_name = os.path.basename(__file__)

def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def read_from_yaml(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print_c('*not a proper print*')
        print_c(e)
        print_c(f"*not a proper print* error reading {file_path} file")
        # raise Exception(e)
        # return [f"error reading {file_path} file", ]



if __name__ == '__main__':
    conf_path = '\\resources\\fuse.yaml'
    root_path = os.path.dirname(os.path.abspath(__file__))
    config = read_from_yaml(root_path + conf_path)
    # list = config['uncommon_modules']
    # for l in list:
    #     print(l)
    # print(f"{config['uncommon_modules']}")
    main()
    # # a = print('sdfsdf')
    # p = psutil.Process(14908)
    # p.terminate()  # or p.kill()
    # # database = r"D:\files\yearV\cloud\reditworthiness_service\resources\main_db2.db"
    # # conn = sqlite3.connect(database)
    # # cur = conn.cursor()
    # # cur.execute("drop table Business_Services")
    # # cur.execute("drop table Sys_Services")
    # #
    # # rows = cur.fetchall()