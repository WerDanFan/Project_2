from flask import Flask, jsonify, request
import requests
import json

API = 'bSxseO5nsaAgbkjld3zBGMnyy3mbZlvr'


class AccuWeather:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.location_key = 3369279 #Moscow

    def send_request(self,lat,lng):

        #location_key = self.get_location_key(lat,lng)

        weather_data = self.get_weather()

        self.info_to_json(weather_data)

    def get_location_key(self,lat,lng):
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={self.api_key}&q={lat},{lng}"
        response = requests.get(location_url)
        location_data = response.json()

        if response.status_code == 200:
            self.location_key = location_data['Key']
        elif response.status_code == 403:
            print('Доступ запрещён: некорректный адрес или координаты')
            exit()
        else:
            print('Произошла ошибка на сервере')
            exit()

    def get_weather(self):
        weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.location_key}?apikey={self.api_key}&details=true&metric=true"
        response = requests.get(weather_url)
        weather_data = response.json()

        if response.status_code == 200:
            return weather_data
        elif response.status_code == 403:
            print('Доступ запрещён: некорректный адрес или координаты')
            exit()
        else:
            print('Произошла ошибка на сервере')
            exit()

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

        with open('weather_info.json', 'w') as f:
            json.dump(result, f, indent=4)


def check_bad_weather(path):
    with open(path, 'r') as f:
        data = json.load(f)
    flag = True
    if data["temperature (max)"] > 35 or data["temperature (min)"] < -15: flag = False
    if data["humidity"] > 90: flag = False
    if data["wind_speed"] > 15: flag = False
    if data["precipitation_probability"] >70: flag = False

    if flag:
        return 'Благоприятные погодные условия'
    else:
        return 'Неблагоприятные погодные условия'



# Moscow = AccuWeather(API)
# Moscow.send_request('55.44', '37.36')
# print(Moscow.location_key)

print(check_bad_weather('weather_info.json'))