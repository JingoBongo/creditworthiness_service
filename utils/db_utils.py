import os
import sqlite3 as sl

root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils','')
sql_connection = sl.connect(root_path+'resources\\main_db.db')


def initial_sys_table_creation():
    with sql_connection:
        sql_connection.execute("""
            CREATE TABLE Sys_Services (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                port TEXT
            );
        """)


def insert_into_sys_services(name, port):
    sql = 'INSERT INTO USER (name, age) values(?, ?)'
    data = [
        (name, port)
    ]
    try:
        with sql_connection:
            sql_connection.executemany(sql, data)
    except Exception as e:
        print(str(e))