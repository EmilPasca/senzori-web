#!/usr/bin/env python3

import requests

url = "https://api.open-meteo.com/v1/forecast?latitude=47.6567&longitude=23.5849&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Europe%2FBucharest"


def main():
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        date = response.json()
        print(f"Temperatura pentru Baia Mare, România: {date['current']['temperature_2m']} °C")
    except requests.RequestException as exc:
        print("Eroare la apelul API:", exc)


if __name__ == "__main__":
    main()
