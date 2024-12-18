# Прогноз погоды: Веб-сервис на Flask с анализом данных

Этот проект представляет собой веб-сервис на базе Flask, который получает данные о погоде через API, анализирует их и отображает информацию о благоприятности погодных условий.

## Функциональность

• **Получение данных:**  Получает прогноз погоды с помощью API (AccuWeather).

• **Анализ данных:**  Анализирует полученные данные, определяя благоприятность погоды на основе заданных критериев (температура, влажность, вероятность осадков, скорость ветра).  Критерии можно настроить в конфигурационном файле.

• **Веб-сервис:**  Предоставляет веб-интерфейс на основе Flask для отображения результатов анализа.  Показывает прогноз погоды в удобном для пользователя формате, включая индикатор благоприятности.


## Технологии

• **Python:** Язык программирования.

• **Flask:**  Фреймворк для создания веб-приложений.

• **Requests:** Библиотека для работы с HTTP запросами (для обращения к API).


## Установка

1. **Клонирование репозитория:**
   
        git clone https://github.com/WerDanFan/Project_2

2. **Создание виртуального окружения (рекомендуется):**

        python3 -m venv venv
        source venv/bin/activate  # Linux/macOS
        venv\Scripts\activate  # Windows

3. **Установка зависимостей:**

        pip install -r requirements.txt

4. **Настройка конфигурации:**

    Заполните необходимые параметры (API ключ).

## Запуск

1. **Запуск веб-сервера:**

        python app.py

2. **Открытие веб-страницы:**
   Перейдите в браузере по адресу http://127.0.0.1:5000/ (или указанному в конфигурации порту).


## Конфигурация (config.py)

• API_KEY:  Ключ API для доступа к сервису погоды.

## Структура проекта
weather_forecast/

├── Api_weather.py          # Основной файл приложения Flask\
├── templates/              # Шаблоны для Flask\
│   ├── first_page.html     # Форма для ввода городов\
│   └── weather_page.html   # Страница для показа благоприятности\
└── requirements.txt        # Список зависимостей

## Лицензия

**MIT**


## Вклад

Вклады приветствуются!  Пожалуйста, создайте pull request после написания кода и прохождения тестов.

## Контакты

**danil_fedotov_06@list.ru**
   
