import os
import sqlite3 as sl

root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
sql_connection = sl.connect(root_path + 'resources\\main_db.db')


def initial_sys_table_creation():
    with sql_connection:
        sql_connection.execute("""
            CREATE TABLE Sys_Services (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                port TEXT,
                pid INTEGER NOT NULL
            );
        """)


def insert_into_sys_services(name, port, pid):
    sql = 'INSERT INTO Sys_Services (name, port, pid) values(?, ?, ?)'
    data = [
        (name, port, pid)
    ]
    try:
        with sql_connection:
            sql_connection.executemany(sql, data)
    except Exception as e:
        print(str(e))


def clear_system_tables():
    with sql_connection:
        sql_connection.execute("""
            DELETE FROM Sys_Services;
        """)

# initial systable creation should be probably done in other place
# initial_sys_table_creation()