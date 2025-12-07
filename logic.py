import sqlite3
from config import DATABASE
from typing import List, Tuple

class DB_Manager:
    def __init__(self, database): 
        self.database = database 

    def _get_conn(self): 
        return sqlite3.connect(self.database, check_same_thread=False) 

    def create_tables(self): 
        conn = self._get_conn()
        with conn:
            # DROP таблиц для полной очистки
            conn.execute("DROP TABLE IF EXISTS Users")
            conn.execute("DROP TABLE IF EXISTS Day_plan")
            conn.execute("DROP TABLE IF EXISTS Notes")
            
            # Создание таблиц заново
            conn.execute("""
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE
            )""")

            conn.execute("""
            CREATE TABLE Day_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Day_plan_task TEXT,
                Day_plan_time VARCHAR,
                plan_date VARCHAR,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            )""")

            conn.execute("""
            CREATE TABLE Notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_text TEXT,
                note_date VARCHAR,
                user_id INTEGER
            )""")
            conn.commit()


    # User helpers
    def ensure_user(self, user_id):
        conn = self._get_conn()
        with conn:
            cur = conn.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
            if cur.fetchone() is None:
                conn.execute(
                    "INSERT INTO Users (user_id) VALUES (?)",
                    (user_id,)
                )
                conn.commit()

    # Day plan
    def save_user_day_plan(self, Day_plan_task, Day_plan_time, user_id, plan_date):
        conn = self._get_conn()
        with conn:
            conn.execute(
                "INSERT INTO Day_plan (Day_plan_task, Day_plan_time, plan_date, user_id) VALUES (?, ?, ?, ?)",
                (Day_plan_task, Day_plan_time, plan_date, user_id)
            )
            conn.commit()

    def get_user_day_plan(self, user_id) -> List[Tuple[int, str, str]]:
        conn = self._get_conn()
        with conn:
            cur = conn.execute(
                "SELECT id, Day_plan_task, Day_plan_time FROM Day_plan WHERE user_id = ? ORDER BY id",
                (user_id,)
            )
            return cur.fetchall()

    def clear_user_day_plan(self, user_id):
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM Day_plan WHERE user_id = ?", (user_id,))
            conn.commit()

    def get_user_day_plan_dates(self, user_id):
        conn = self._get_conn()
        with conn:
            cur = conn.execute("SELECT DISTINCT plan_date FROM Day_plan WHERE user_id = ? ORDER BY plan_date", (user_id,))
            return [row[0] for row in cur.fetchall()]
    
    def get_user_day_plan_by_date(self, user_id: int, plan_date: str):
        conn = self._get_conn()
        with conn:
            cur = conn.execute(
                "SELECT id, Day_plan_task, Day_plan_time FROM Day_plan WHERE user_id = ? AND plan_date = ? ORDER BY id",
                (user_id, plan_date)
            )
            return cur.fetchall()

    # Notes
    def save_user_note(self, note_text, note_date, user_id):
        conn = self._get_conn()
        with conn:
            conn.execute(
                "INSERT INTO Notes (note_text, note_date, user_id) VALUES (?, ?, ?)",
                (note_text, note_date, user_id)
            )
            conn.commit()

    def get_user_notes(self, user_id: int):
        conn = self._get_conn()
        with conn:
            cur = conn.execute(
                "SELECT id, note_text, note_date FROM Notes WHERE user_id = ? ORDER BY id",
                (user_id,)
            )
            return cur.fetchall()
            
    def delete_user_note(self, user_id: int, note_id: int):
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM Notes WHERE user_id = ? AND id = ?", (user_id, note_id))
            conn.commit()
    
    
    # def clear_user_notes(self, user_id: int):
    #     conn = self._get_conn()
    #     with conn:
    #         conn.execute("DELETE FROM Notes WHERE user_id = ?", (user_id,))
    #         conn.commit()