
import sqlite3
from datetime import date


class DatabaseManager:
    connection = None
    cursor = None
    def __init__(self):
        self.connection, self.cursor = self.init_connection()
        self.create_logs_table()

    def init_connection(self):
        connection = sqlite3.connect('gbgs_logs.db')
        return connection, connection.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def create_logs_table(self):
        query = """CREATE TABLE IF NOT EXISTS
        logs(id  INTEGER PRIMARY KEY, date TIMESTAMP, message TEXT)
        """
        return self.execute_query(query)

    def insert_log(self, message):
        # query = f"""
        #     INSERT INTO logs VALUES ({None}, {date.today()}, {message})
        # """
        query = f"INSERT INTO logs VALUES(NULL, date('{date.today()}'), '{message}')"
        self.execute_query(query)
        self.connection.commit()

    def get_last_week_logs(self):
        query = f"""select * from logs
        where date > date('{date.today()}', '-7 day')
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

"""
    How to use:
    1- create an object
    database_manager = DatabaseManager()
    this object will create the database and the table if they are not existed
    
    2- to insert a log
    database_manager.insert_log("New address has been added")
    this function will also take the current date from the system

"""
""" This is an automatic mail
    Update of gpgs
"""
database_manager = DatabaseManager()
database_manager.insert_log("New address has been added")
print(database_manager.get_last_week_logs())

# Tomorrow show the frontend

