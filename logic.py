import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database, check_same_thread=False)
        with conn:

            conn.execute("""CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_name TEXT,
                        user_password VARCHAR
                        )""")
            
            conn.execute("""CREATE TABLE IF NOT EXISTS Tasks (
                        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        task_name TEXT,
                        task_data VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id)
                        )""")
            
            conn.execute("""CREATE TABLE IF NOT EXISTS New_habits (
                        new_habitid INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        new_habitid_time VARCHAR,
                        new_habitid_name TEXT,
                        new_habitid_tekst TEXT,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id)
                        )""")

            conn.commit()


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()