from flask import Flask, request, render_template
import requests
import json
import os

API = "bSxseO5nsaAgbkjld3zBGMnyy3mbZlvr"


class AccuWeather:
    """
    Класс для работы с погодой
    """
    def __init__(self, api_key: str, path: str):
        self.api_key = api_key
        self.location_key = 0
        self.path = path

    def send_request(self, city: str):
        """
        Получает информацию и сохраняет в JSON
        :param city: название города
        """
        self.check_location_key(city)
        weather_data = self.get_weather()
        self.info_to_json(weather_data)

    def check_location_key(self,city: str):
        """
        Проверяет наличие ключа у введенного города
        :param city: название города
        """
        if os.path.exists('keys_of_cities.json'):
            with open('keys_of_cities.json', 'r', encoding='utf-8') as f:
                keys = json.load(f)
                if city in keys:
                    self.location_key = keys[city]
                else:
                    self.get_location_key(city)
        else: self.get_location_key(city)

    def load_city_keys(self) -> dict:
        """
        Загружает ключи городов из JSON файла в словарь
        :return: словарь вида {city_name: key ...}
        """
        if os.path.exists('keys_of_cities.json'):
            with open('keys_of_cities.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}

    def save_city_keys(self, city_keys: dict):
        """
        Сохраняет JSON файл
        :param city_keys: словарь вида {city_name: key ...}
        """
        with open('keys_of_cities.json', 'w', encoding="utf-8") as f:
            json.dump(city_keys, f, indent=4)

    def get_location_key(self, city: str):
        """
        Посылает запрос и получает ключ введенного города
        :param city: название города
        """
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={self.api_key}&q={city}"
        response = requests.get(location_url)
        location_data = response.json()

        if location_data:
            if response.status_code == 200:
                self.location_key = location_data[0]["Key"]
                keys = self.load_city_keys()
                keys[city] = self.location_key
                self.save_city_keys(keys)
            elif response.status_code == 403:
                raise Exception("Упс. Неверный API key")
            elif response.status_code == 503:
                raise Exception("Упс. Закончились запросы API. Попробуйте позже.")
            else:
                raise Exception(f"Произошла ошибка на сервере {response.status_code}")
        else:
            raise Exception("Упс. Неверно введён город")

    def get_weather(self):
        """
        Посылает запрос и получает погоду по ключу (self.location_key)
        """
        weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.location_key}?apikey={self.api_key}&details=true&metric=true"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data:
            if response.status_code == 200:
                return weather_data
            elif response.status_code == 403:
                raise Exception("Упс. Неверный API key")
            elif response.status_code == 503:
                raise Exception("Упс. Закончились запросы API. Попробуйте позже.")
            else:
                raise Exception(f"Произошла ошибка на сервере {response.status_code}")
        else:
            raise Exception("Упс. Неверно введён город")


    def info_to_json(self, data: dict):
        """
        Загрузка погодных условий в JSON файл
        :param data: данные о погоде
        """
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


def check_bad_weather(path: str) -> str:
    """
    Логика для определения благоприятности погодных условий
    :param path: ссылка на JSON файл с погодными условиями
    :return: Статус погодных условий (Благоприятные/Неблагоприятные погодные условия)
    """
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
            city_2.send_request(end_city)
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
