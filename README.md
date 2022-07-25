![](https://img.shields.io/badge/version-v0.4.2-gold)  
![](https://img.shields.io/badge/python-v3.10.1-blue)
![](https://img.shields.io/badge/Flask-v2.1.3-pink)
![](https://img.shields.io/badge/sqlite3-v2.6.0-purple)
![](https://img.shields.io/badge/Docker-v20.10.17-orange)

![](https://img.shields.io/badge/pytest-v7.1.2-black)
![](https://img.shields.io/badge/passed_tests-12-brightgreen)
![](https://img.shields.io/badge/failed_tests-0-red)

![](https://img.shields.io/badge/coverage-100%25-brightgreen)

---

- [Solution Tree](#solution-tree)  
- [How To Run Locally](#how-to-run-locally)
- [How To Run With Docker](#how-to-run-with-docker)
- [Making Requests](#making-requests)
- [FYI](#fyi)
  - [Additional Information](#additional-information)
  - [What Did Go Right](#what-did-go-rigth)
  - [What Did Go Wrong](#what-did-go-wrong)
  - [Doubts](#doubts)

# Solution Tree

## The `app.py` module
The running process occurs in `app.py`. Module responsible for doing the entire Flask process.

As requested in the challenge, this API works with two methods. One `GET` and one `POST`. Both handled through the `/weather` route.
```
@app.route("/weather", methods=['GET', 'POST'])
```

## The `POST` method
Responsible for receiving a user defined id, and from that, making pre-defined requests to the Open Weather API.
Then store the response, so it can be consulted later.

After evaluating that the received request is a POST. The first thing the function does, is to get the `user_id`, from the body.
```
    if request.method == "POST":
        request_data = request.json

        try:
            user_id = request_data["id"]
        except KeyError:
            return {"message": "Missing param 'id'."}, 400
```
As we can see above, if the `id` param is not in the requested body, it will return an error.

After that, we call another function, responsible for validating the `user_id`. And only if the `user_id` is valid, we continue on the code.
```
if verify_user_id(user_id):
.
.
.
else:
    return {"message": "Invalid ID. It must contain only numbers and be unique."}, 400
```
>The `verify_user_id()` function checks every path possible for evaluating the `user_id`
> ```
> def verify_user_id(user_id):
>    try:
>        user_id = int(user_id)
>    except ValueError:
>        return False
>    except TypeError:
>        return False
>
>    sql = "SELECT user_id FROM weather"
>    db = db_connect()
>    cur = db.cursor()
>    cur.execute(sql)
>    rows = cur.fetchall()
>
>    for row in rows:
>        if user_id == row[0]:
>            return False
>
>    return True
> ```
> First, we try to convert it into an integer, because the `id` must contain only numbers, if it's not converted, we return `False`.
>
> Then, we query through de database, and check if there's already collected cities with this id (`user_id` is not unique, but it can only call API `POST` method once).

If everything is valid with the `user_id`, we can move on.

First, we get the request datetime, then generate a list with all the cities to collect. For doing so, we use another two functions `get_weather()` and `insert_weather()`
```
request_datetime = datetime.now()

cities = os.getenv("APPENDIX_A").split(',')
try:
    for city_id in cities:
        city_info = get_weather(city_id)
        insert_weather(user_id, request_datetime, str(city_info))
except Exception as e:
    return {"message": e}, 500
```
>The `get_weather()` function, calls the Open Weather API and returns the desired information.
> ```
> def get_weather(city_id):
>    weather_api = os.getenv('WEATHER_API')
>    api_key = os.getenv('API_KEY')
>
>    query = f"id={city_id}&appid={api_key}"
>
>    url = weather_api + query
>
>    data = requests.get(url).json()
>
>    return {
>        "city_id": data['id'],
>        "temp": data['main']['temp'],
>        "humidity": data['main']['humidity']
>    }
> ```
>
> The `insert_weather()` function picks all the information and insert them to the database
> ```
> def insert_weather(user_id, request_datetime, city_info):
>    sql = f'''
>    INSERT INTO weather(user_id, collected_at, city_info)
>    VALUES({user_id}, datetime("{request_datetime}"), ?)
>    '''
>
>    db = db_connect()
>    cur = db.cursor()
>    cur.execute(sql, (city_info,))
>    db.commit()
> ```

If any of this process go wrong, we return an error 500, because in this case, it must be a system error.

But if everything goes right we return a success message
```
return {"message": "All cities collected."}, 200
```

---

## The `GET` method
Responsible for receiving a `user_id`, and query through the database. Checking if the collecting method is completed. If not, we return the percentage of the process.

After evaluating that the received request is a `GET`. The first thing the function does, is to get the `user_id`, from the `url-query`.
```
if request.method == "GET":
    user_id = request.args.get("id")

    if not user_id:
        return {"message": "Missing query param 'id'."}, 400
```
The first thing that we check, is if the `id` param is present on the query url. If not, e return an error.

After that we check if the `user_id` is valid, by trying to convert it to an integer.
```
try:
    int(user_id)
except ValueError:
    return {"message": "Invalid ID. It must contain only numbers and be unique."}, 400
```

Then, we call `get_collected_cities()` function, which will try to get and return the cities caught by the POST request.
```
collected_cities = get_collected_cities(user_id)
```
> This method queries in database with the received `user_id`, and at first checks if it has rows. If not, we return a `False` statement.
> ```
> def get_collected_cities(user_id):
>    sql = f'''
>        SELECT collected_at, city_info FROM weather
>        WHERE user_id = {user_id}
>        '''
>
>    db = db_connect()
>    cur = db.cursor()
>    cur.execute(sql)
>    rows = cur.fetchall()
>
>    print(rows)
>    if len(rows) == 0:
>        return False
> ```
> If the query returns data, we compare the current number of collected cities, with the number of cities requested. And with this information, we can get the percentage.
> ```
>    collected_info = {}
>
>    cities_ids = os.getenv("APPENDIX_A").split(',')
>    progress = (len(rows) * 100) / len(cities_ids)
>
>    collected_info["user_id"] = user_id
>    collected_info["progress"] = f"{progress:.3g}%"
> ```
> Finishing, we get the information received from the database, and mount a `json object` for showing to the user.
> ```
>    cities = []
>    for row in rows:
>        city_info = row[1].replace("\'", "\"")
>        city_info = json.loads(city_info)
>        data_info = city_info
>        data_info["collected_at"] = row[0]
>
>        cities.append(data_info)
>
>    collected_info["cities"] = cities
>    return collected_info
> ```

If there were no data for the passed `id`, we return this error message, but if it has we return the object with the percentage and the cities collected.
```
if not collected_cities:
    return {"message": "User identifier not found."}, 400

return collected_cities, 200
```

# How To Run Locally
Requirements:
- [Git](https://git-scm.com/downloads)
- [Python3.10](https://www.python.org/downloads/)
- .env file containing the private access-token and the cities ids to Open Weather API _(you can ask this file to the project mantainer)_

1. Clone the repository  
`https://github.com/salatiel6/devgrid_challenge.git`


2. Open the challenge directory  
Widows/Linux:`cd devgrid_challenge`  
Mac: `open devgrig_challenge`


3. Create virtual environment (recommended)  
`python -m venv ./venv`


4. Activate virtual environment (recommended)  
Windows: `venv\Scripts\activate`  
Linux/Mac: `source venv/bin/activate`


5. Install every dependencies  
`pip install -r requirements.txt`


6. Open the tests' directory  
Windows/Linux: `cd tests`  
Mac: `open tests`


7. Run tests  
Without coverage: `pytest`  
With coverage: `pytest -vv --cov=. --cov-report=term-missing --cov-config=.coveragerc`


8. Get back at root directory
`cd ..`


9. Open the source directory  
Windows/Linux: `cd src`  
Mac: `open src`


10. Run the application  
`python app.py`

# How To Run With Docker
This application was developed in a Windows OS. So I'm not sure if Linux or Mac can run the container.

Requirements:
- [Git](https://git-scm.com/downloads)
- [Docker](https://www.docker.com/)
- .env file containing the private access-token and the cities ids to Open Weather API _(you can ask this file to the project mantainer)_

1. Clone the repository  
`https://github.com/salatiel6/devgrid_challenge.git`


2. Open the challenge directory  
Widows/Linux:`cd devgrid_challenge`  
Mac: `open devgrig_challenge`


3. Build docker image  
`docker-compose build`


4. Start docker container  
`docker-compose up -d`

# Making Requests
Recommended: 
- [Postman](https://www.postman.com/)  

After starting the application, with or without docker, it should be running at your `localhost`

## Endpoints

Search and insert weather:
> ![](https://img.shields.io/badge/method-POST-purple)  
> `url`: `http://localhost:5000/weather`  
>
> `body example`:
> ```
> {
>     "id": "123456"
> }
> ```

Get collected cities:
> ![](https://img.shields.io/badge/method-GET-pink)  
> 
> `query-url example`:  
> `url`: `http://localhost:5000/weather?id=123456`

**Note**: A valid `id` must contain only numbers and be unique when calling the POST method.

# FYI
## Additional Information
- `.env`: Configuration file that is not on the repository but is needed to run the application. Because it has the access token, and the cities ids to make request to Open Weather API. _(you can ask this file to the project mantainer)_  
- `pre-commit-config.yaml`: File which uses flake8 that is a python tool that glues together pycodestyle, pyflakes, mccabe, and third-party plugins to check the style and quality of some python code. It can be installed within git, so you can't commit anything out of the PEP 8 patterns.  
- `sqlite3`: Was chosen as the application database because of its simplicity and availability to run within Python and Docker.

## What Did Go Rigth
- Application runnig in local machine
- Application runnig in local docker image
- Database storing all the information requested
- Application and Database tests running with 100% pytest coverage

## What Did Go Wrong
- Couldn't split `app.py` in desired multiple modules(`run.py`, `views.py`, `features.py`). Because when running in Docker, it couldn't import these modules. It probably has something to do with PYTHONPATH, but I wasn't able to solve this problem.

## Doubts
- I don't know if I handled SQLite database files on propper way.
- The pytest coverage returns 100%. But I'm  not sure if everything is properly tested.
- Got some problems when trying to split app.py module, and I don't know what is the real problem.