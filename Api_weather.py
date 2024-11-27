from flask import Flask, request, render_template
import requests
import json
import os

API = "bSxseO5nsaAgbkjld3zBGMnyy3mbZlvr"


class AccuWeather:
    def __init__(self, api_key, path):
        self.api_key = api_key
        self.location_key = 0
        self.path = path

    def send_request(self, city):
        self.check_location_key(city)
        weather_data = self.get_weather()
        self.info_to_json(weather_data)

    def check_location_key(self,city):
        if os.path.exists('keys_of_cities.json'):
            with open('keys_of_cities.json', 'r') as f:
                keys = json.load(f)
                if city in keys:
                    self.location_key = keys[city]
                else:
                    self.get_location_key(city)

    def load_city_keys(self):
        if os.path.exists('keys_of_cities.json'):
            with open('keys_of_cities.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_city_keys(self, city_keys):
        with open('keys_of_cities.json', 'w') as f:
            json.dump(city_keys, f, indent=4)

    def get_location_key(self, city):
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={self.api_key}&q={city}"
        response = requests.get(location_url)
        location_data = response.json()

        if response.status_code == 200:
            self.location_key = location_data[0]["Key"]
            keys = self.load_city_keys()
            keys[city] = self.location_key
            self.save_city_keys(keys)
        elif response.status_code == 403:
            raise Exception("Упс. Неверно введён город")
        else:
            raise Exception("Произошла ошибка на сервере")

    def get_weather(self):
        weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.location_key}?apikey={self.api_key}&details=true&metric=true"
        response = requests.get(weather_url)
        weather_data = response.json()

        if response.status_code == 200:
            return weather_data
        elif response.status_code == 403:
            raise Exception("Упс. Неверно введён город")
        else:
            raise Exception("Произошла ошибка на сервере")

    def info_to_json(self, data):
        temperature_min = data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
        temperature_max = data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
        humidity = data["DailyForecasts"][0]["Day"]["RelativeHumidity"]["Average"]
        wind_speed = data["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"]
        precipitation_probability = data["DailyForecasts"][0]["Day"]["PrecipitationProbability"]

        result = {
            "temperature (max)": temperature_max,
            "temperature (min)": temperature_min,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "precipitation_probability": precipitation_probability,
        }

        with open(self.path, "w") as f:
            json.dump(result, f, indent=4)


def check_bad_weather(path):
    with open(path, "r") as f:
        data = json.load(f)
    flag = True
    if data["temperature (max)"] > 35 or data["temperature (min)"] < -15:
        flag = False
    if data["humidity"] > 90:
        flag = False
    if data["wind_speed"] > 15:
        flag = False
    if data["precipitation_probability"] > 70:
        flag = False

    if flag:
        return "Благоприятные погодные условия"
    else:
        return "Неблагоприятные погодные условия"


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def write_city():
    if request.method == "GET":
        return render_template("first_page.html")
    else:
        start_city = request.form["startPoint"]
        end_city = request.form["endPoint"]

        city_1 = AccuWeather(API, "city_1.json")
        try:
            city_1.send_request(start_city)
            status_city_1 = check_bad_weather("city_1.json")
        except Exception as exc:
            status_city_1 = exc

        city_2 = AccuWeather(API, "city_2.json")
        try:
            city_2.send_request(start_city)
            status_city_2 = check_bad_weather("city_2.json")
        except Exception as exc:
            status_city_2 = exc

        if os.path.exists("city_1.json"):
            os.remove("city_1.json")
        if os.path.exists("city_2.json"):
            os.remove("city_2.json")

        return render_template(
            "weather_page.html",
            status_city_1=status_city_1,
            status_city_2=status_city_2,
            city_1=start_city,
            city_2=end_city,
        )


if __name__ == "__main__":
    app.run(debug=True)
