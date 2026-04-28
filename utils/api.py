import requests

def get_exchange_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            usd_to_kzt = 459.47
            rates = data.get("rates", {})
            eur_to_kzt = round(usd_to_kzt / rates.get("EUR", 1.0) * rates.get("EUR", 1.0), 2)
            rub_to_kzt = round(usd_to_kzt / rates.get("RUB", 1.0) * rates.get("RUB", 1.0), 2)
            cny_to_kzt = round(usd_to_kzt / rates.get("CNY", 1.0) * rates.get("CNY", 1.0), 2)
            return {"USD": usd_to_kzt, "EUR": eur_to_kzt, "RUB": rub_to_kzt, "CNY": cny_to_kzt}
    except:
        pass
    return {"USD": 459.47, "EUR": 538.89, "RUB": 6.13, "CNY": 67.23}

def get_weather():
    cities = [
        {"name": "Атырау", "lat": 47.1167, "lon": 51.8833},
        {"name": "Актау", "lat": 43.65, "lon": 51.1667},
        {"name": "Кульсары", "lat": 46.95, "lon": 53.9833},
        {"name": "Уральск", "lat": 51.2333, "lon": 51.3667},
        {"name": "Актобе", "lat": 50.2833, "lon": 57.1667},
    ]
    weather_data = []
    for city in cities:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_data.append({"city": city["name"], "temp": data["current_weather"]["temperature"]})
        except:
            weather_data.append({"city": city["name"], "temp": None})
    return weather_data
