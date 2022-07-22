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


def db_connect():
    db = None
    try:
        db = sqlite3.connect(os.getenv('DATABASE'))
    except Exception as e:
        print(e)

    return db


@app.route("/")
def index():
    return "Index"


@app.route("/weather", methods=['GET', 'POST'])
def weather():
    if request.method == "POST":
        request_data = request.json
        user_id = int(request_data["id"])
        if verify_user_id(user_id):

            request_datetime = datetime.now()

            cities = os.getenv("APENDIX_A").split(',')
            for city_id in cities:
                city_info = get_weather(city_id)
                insert_weather(user_id, request_datetime, str(city_info))

            return "done"
        else:
            return "invalid id"
    if request.method == "GET":
        user_id = request.args.get("id")

        collected_cities = get_collected_cities(user_id)

        return collected_cities


def verify_user_id(user_id):
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
    weather_api = os.getenv('WEATHER_API')
    api_key = os.getenv('API_KEY')

    query = f"id={city_id}&appid={api_key}"

    url = weather_api + query

    data = requests.get(url, verify=False).json()

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

    collected_info = {}

    cities_ids = os.getenv("APENDIX_A").split(',')
    progress = (len(rows) * 100) / len(cities_ids)

    collected_info["user_id"] = user_id
    collected_info["progress"] = str(progress) + "%"

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
    app.run(debug=True, host="0.0.0.0", port=5000)
