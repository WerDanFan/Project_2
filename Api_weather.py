import pandas as pd
import requests
import datetime
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


def check_bad_weather(temperature_min, temperature_max, humidity, wind_speed, precipitation_probability):
    flag = True
    if temperature_max > 35 or temperature_min < -15:
        flag = False
    if humidity > 90:
        flag = False
    if wind_speed > 15:
        flag = False
    if precipitation_probability > 70:
        flag = False

    if flag:
        return "Благоприятные погодные условия"
    else:
        return "Неблагоприятные погодные условия"


def date_parser(date):
    dt_object = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    date_only = dt_object.date()
    return date_only

class Weather:

    api_key = 'l3LC5vveUNQo1Y0hCGjZwIxTpiGVoxLw'


    def __init__(self):
        self.all_forecasts = pd.DataFrame(columns=['city', 'date', 'temperature (max)','temperature (min)', 'humidity', 'wind_speed', 'precipitation_probability', 'good/bad', 'lat', 'lon'])
        self.all_cords = {}
        self.all_keys = {}

    def get_keys_and_cords(self, cities):
        for city in cities:
            if city in self.all_keys:
                pass

            else:
                location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={self.api_key}&q={city}"
                response = requests.get(location_url)
                data = response.json()

                if data:
                    if response.status_code == 200:
                        key = data[0]["Key"]
                        lat = data[0]["GeoPosition"]["Latitude"]
                        lon = data[0]["GeoPosition"]["Longitude"]

                        self.all_keys[city] = key
                        self.all_cords[city] = [lat,lon]

                    elif response.status_code == 403:
                        raise Exception("Упс. Неверный API key")
                    elif response.status_code == 503:
                        raise Exception("Упс. Закончились запросы API. Попробуйте позже.")
                    else:
                        raise Exception(f"Произошла ошибка на сервере {response.status_code}")

                else:
                    raise Exception(f"Упс. Неверно введён один из городов: {city}")


    def add_forecasts_in_all_forecasts(self, cities):
        for city in cities:
            if city in self.all_forecasts['city'].unique():
                pass

            else:
                weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{self.all_keys[city]}?apikey={self.api_key}&details=true&metric=true"
                response = requests.get(weather_url)
                data = response.json()

                if data:
                    if response.status_code == 200:

                        for i in range(5):
                            date = date_parser(data["DailyForecasts"][i]["Date"])
                            temperature_min = data["DailyForecasts"][i]["Temperature"]["Minimum"]["Value"]
                            temperature_max = data["DailyForecasts"][i]["Temperature"]["Maximum"]["Value"]
                            humidity = data["DailyForecasts"][i]["Day"]["RelativeHumidity"]["Average"]
                            wind_speed = data["DailyForecasts"][i]["Day"]["Wind"]["Speed"]["Value"]
                            precipitation_probability = data["DailyForecasts"][i]["Day"]["PrecipitationProbability"]
                            lat = self.all_cords[city][0]
                            lon = self.all_cords[city][1]

                            row = {'city': city,
                                   'date': date,
                                   'temperature (max)': temperature_min,
                                   'temperature (min)': temperature_max,
                                   'humidity': humidity,
                                   'wind_speed': wind_speed,
                                   'precipitation_probability': precipitation_probability,
                                   'good/bad': check_bad_weather(temperature_min,
                                                                 temperature_max,
                                                                 humidity,
                                                                 wind_speed,
                                                                 precipitation_probability),
                                   'lat': lat,
                                   'lon': lon}

                            self.all_forecasts.loc[len(self.all_forecasts)] = row


                    elif response.status_code == 403:
                        raise Exception("Упс. Неверный API key")
                    elif response.status_code == 503:
                        raise Exception("Упс. Закончились запросы API. Попробуйте позже.")
                    else:
                        raise Exception(f"Произошла ошибка на сервере {response.status_code}")
                else:
                    raise Exception("Пустая data при вызове погоды")


    def filter(self,cities):
        df = self.all_forecasts[self.all_forecasts['city'].isin(cities)]
        return df

    def get_df(self,cities):
        error_bool = False
        try:
            self.get_keys_and_cords(cities)
            self.add_forecasts_in_all_forecasts(cities)
            df = self.filter(cities)
            return error_bool, df

        except Exception as e:
            error_bool = True
            return error_bool, e



def generate_graphs(df, days, cities):
    day = datetime.datetime.now().date() + datetime.timedelta(days=days)

    filtered_df = df[df['date'] <= day] if day else df

    fig_temp = go.Figure()
    fig_hum = go.Figure()
    fig_wind = go.Figure()
    fig_rain = go.Figure()

    for city in cities:
        df_city = filtered_df[filtered_df['city'] == city]

        fig_temp.add_trace(go.Scatter(x=df_city["date"], y=df_city["temperature (max)"], name=city))
        fig_hum.add_trace(go.Scatter(x=df_city["date"], y=df_city["humidity"], name=city))
        fig_wind.add_trace(go.Scatter(x=df_city["date"], y=df_city["wind_speed"], name=city))
        fig_rain.add_trace(go.Scatter(x=df_city["date"], y=df_city["precipitation_probability"], name=city))


    fig_temp.update_layout(yaxis_title='Температура(C˚)',
                           title='Температура в городах по дням')
    fig_hum.update_layout(yaxis_title='Влажность(%)',
                          title='Влажность в городах по дням')
    fig_wind.update_layout(yaxis_title='Скорость ветра(м/с)',
                           title='Скорость ветра в городах по дням')
    fig_rain.update_layout(yaxis_title='Вероятность осадков(%)',
                           title='Вероятность осадков в городах по дням')

    df_cords = filtered_df[filtered_df['date'] == day]
    map_cities = px.scatter_map(df_cords, lat="lat", lon="lon", color='good/bad',zoom=1,hover_name="city")
    map_cities.update_layout(title='Прогноз погоды на карте', showlegend=False)

    return fig_temp, fig_hum, fig_wind, fig_rain, map_cities




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    html.H1("Сервис просмотра погоды", className='text-center text-primary mb-4',
            style={'fontSize': '64px', 'height': '90px', 'fontWeight': 'bold'}),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([html.Label("Количество дней в прогнозе:"),
                    dcc.Slider(0, 4, 1, value=2, id='slider_of_days')], md=6),
                dbc.Col([
                    dbc.Row([
                        dcc.Input(id="input", type="text", placeholder="Например: Москва,Тула", debounce=True, style={'width': '300px'}),
                        html.Button('Отправить', id='submit-button')
                    ])
                ], md=4)
            ]),

            dbc.Row([
                dbc.Col([dcc.Graph(id='mapbox')], md=12)
            ])
        ]),

        dbc.Col([dcc.Graph(id='temp-graph')], md=4)
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='hum-graph')], md=4),
        dbc.Col([dcc.Graph(id='wind-graph')], md=4),
        dbc.Col([dcc.Graph(id='rain-graph')], md=4)
        ]),

])




# Коллбэки для обновления статистики и графиков
@app.callback(
    [Output('temp-graph', 'figure'),
     Output('hum-graph', 'figure'),
     Output('wind-graph', 'figure'),
     Output('rain-graph', 'figure'),
     Output('mapbox', 'figure')],
    [Input('slider_of_days', 'value'),
     Input('input', 'value'),
     #Input('submit-button', 'n_clicks')
     ]
)
def update_dashboard(days, cities):
    # if click is not None:

    if cities:
        cities = cities.split(',')
        cities = [city.title() for city in cities]
    else:
        cities = ['Moscow', 'Tula']


    error, data = weather.get_df(cities)

    if not error:
        fig_temp, fig_hum, fig_wind, fig_rain, mapbox = generate_graphs(data, days, cities)
        return fig_temp, fig_hum, fig_wind, fig_rain, mapbox
    else:
        print(f"Ошибка в callback-функции: {data}")
        return (go.Figure(),go.Figure(), go.Figure(), go.Figure(),
                go.Figure().update_layout(title=f"Произошла неизвестная ошибка: {data}"))

# Запуск приложения
if __name__ == '__main__':
    weather = Weather()
    app.run_server(debug=True, use_reloader=True)