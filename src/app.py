import json
import os
import sqlite3
import requests

from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route("/")
def index():
    return "Index"


@app.route("/weather", methods=['GET', 'POST'])
def weather():
    if request.method == "POST":
        request_data = request.json

        try:
            user_id = request_data["user_id"]
        except KeyError:
            return {"message": "Missing param 'user_id'."}, 400

        if verify_user_id(user_id):

            request_datetime = datetime.now()

            cities = get_appendix()
            try:
                for city_id in cities:
                    city_info = get_weather(city_id)
                    insert_weather(user_id, request_datetime, str(city_info))
            except Exception as e:
                return {"message": e}, 500

            return {"message": "All cities collected."}, 200
        else:
            return {"message": "Invalid 'user_id'. It must contain only "
                               "numbers and be unique."}, 400

    if request.method == "GET":
        user_id = request.args.get("user-id")

        if not user_id:
            return {"message": "Missing query param 'user-id'."}, 400

        try:
            int(user_id)
        except ValueError:
            return {"message": "Invalid 'user-id'. It must contain only "
                               "numbers and be unique."}, 400

        collected_cities = get_collected_cities(user_id)

        if not collected_cities:
            return {"message": "User identifier not found."}, 400

        return collected_cities, 200


def env_exisits():
    return os.path.exists("./.env")


def db_connect():
    db = None

    path = "../db"

    if not os.path.exists(path):
        os.makedirs(path)

    try:
        if app.config['TESTING']:
            db = sqlite3.connect("../db/test_sqlite.db")
        else:
            db = sqlite3.connect("../db/sqlite.db")
    except Exception as e:
        print(e)

    return db


def create_db():
    sql = '''
            CREATE TABLE IF NOT EXISTS weather(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                collected_at DATETIME NOT NULL,
                city_info VARCHAR NOT NULL
        )
        '''
    db = db_connect()
    cur = db.cursor()
    cur.execute(sql)
    db.commit()


def get_appendix():
    if app.config['TESTING']:
        appendix = os.getenv("APPENDIX_TEST").split(',')
    else:
        appendix = os.getenv("APPENDIX_A").split(',')

    return appendix


def verify_user_id(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return False
    except TypeError:
        return False

    sql = "SELECT user_id FROM weather"
    db = db_connect()
    cur = db.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    for row in rows:
        if user_id == row[0]:
            return False

    return True


def get_weather(city_id):
    api_key = os.getenv('API_KEY')

    weather_api = "https://api.openweathermap.org/data/2.5/weather"
    query = f"?id={city_id}&appid={api_key}&units=metric"

    url = weather_api + query

    data = requests.get(url).json()

    return {
        "city_id": data['id'],
        "temp": data['main']['temp'],
        "humidity": data['main']['humidity']
    }


def insert_weather(user_id, request_datetime, city_info):
    sql = f'''
    INSERT INTO weather(user_id, collected_at, city_info)
    VALUES({user_id}, datetime("{request_datetime}"), ?)
    '''

    db = db_connect()
    cur = db.cursor()
    cur.execute(sql, (city_info,))
    db.commit()


def get_collected_cities(user_id):
    sql = f'''
        SELECT collected_at, city_info FROM weather
        WHERE user_id = {user_id}
        '''

    db = db_connect()
    cur = db.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    if len(rows) == 0:
        return False

    collected_info = {}

    cities_ids = get_appendix()
    progress = (len(rows) * 100) / len(cities_ids)

    collected_info["user_id"] = user_id
    collected_info["progress"] = f"{progress:.3g}%"

    cities = []
    for row in rows:
        city_info = row[1].replace("\'", "\"")
        city_info = json.loads(city_info)
        data_info = city_info
        data_info["collected_at"] = row[0]

        cities.append(data_info)

    collected_info["cities"] = cities
    return collected_info


if __name__ == "__main__":
    if not env_exisits():
        raise FileNotFoundError(
            ".env not found. Please make sure to get the file with the "
            "project maintainer and attatch to devgrid_challenge/src/ "
            "directory"
        )

    create_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
