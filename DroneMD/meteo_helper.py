import subprocess
import json
import pandas as pd

def meteo(lat, lon, begin, end, model):
        """
        Return historical meteo.
        
        For more info please check : https://open-meteo.com/en/docs/historical-weather-api
        
        Parameters
        ----------
        lat: decimal degree latitude
        lon: decimal degree longitude
        begin: start date YYYY-MM-DD
        end: end date YYYY-MM-DD
        model: era5, era5_land, cerra, best_match
        
        e.g.: meteo(-12.630328, 45.151617, '2022-09-11', '2022-09-11', 'best_match')
        """
        print("Location: " + lat + ", " + lon)
        print("Begin: " + begin + " - End: " + end)
        print("Model: " + model)
        dct = subprocess.check_output(['curl', f'https://archive-api.open-meteo.com/v1/archive?models={model}&latitude={lat}&longitude={lon}&start_date={begin.split(" ")[0]}&end_date={end.split(" ")[0]}&hourly=temperature_2m,relativehumidity_2m,pressure_msl,cloudcover,windspeed_10m,winddirection_10m,windspeed_100m,winddirection_100m,rain']).decode()
        dct = json.loads(dct)
        df = (pd.DataFrame([
            dct['hourly']['temperature_2m'], 
            dct['hourly']['relativehumidity_2m'],
            dct['hourly']['pressure_msl'],
            dct['hourly']['cloudcover'],
            dct['hourly']['windspeed_10m'],
            dct['hourly']['winddirection_10m'],
            dct['hourly']['windspeed_100m'],
            dct['hourly']['winddirection_100m'],
            dct['hourly']['rain'],
            dct['hourly']['time']
            ], index = [
                'T°',
                'Humidity',
                'hPa',
                'CloudCover',
                'WindSpd-10m',
                'WindDir-10m',
                'WindSpd-100m',
                'WindDir-100m',
                'Rain',
                'date'])
        .T
        .assign(date = lambda x : pd.to_datetime(x.date, format='%Y-%m-%dT%H:%M'))
        .set_index(['date']).dropna())
        return df
