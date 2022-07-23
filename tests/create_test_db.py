import sqlite3
import random

from datetime import datetime

def db_connect():
    db = None
    try:
        db = sqlite3.connect("test_sqlite.db")
    except Exception as e:
        print(e)

    return db


def weather_exists():
    sql = '''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='weather';
    '''

    db = db_connect()
    cur = db.cursor()
    cur.execute(sql)
    row = cur.fetchall()

    if len(row) == 1:
        return True

    return False


def create_test_db():
    if not weather_exists():
        db = db_connect()
        cur = db.cursor()

        create_table = '''
                CREATE TABLE weather(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    collected_at DATETIME NOT NULL,
                    city_info VARCHAR NOT NULL
            )
            '''

        cur.execute(create_table)

        for i in range(0, 3):
            user_id = 111111
            request_datetime = datetime.now()
            city_info = {
                "city_id": str(random.randrange(100000, 999999)),
                "temp": str(random.randrange(-70, 50)),
                "humidity": str(random.randrange(50, 100))
            }

            insert = f'''
                    INSERT INTO weather(user_id, collected_at, city_info)
                    VALUES({user_id}, datetime("{request_datetime}"), ?)
                '''

            cur.execute(insert, (str(city_info),))

        db.commit()
