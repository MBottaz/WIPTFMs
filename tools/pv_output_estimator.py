import requests

def pv_output(
    latitude,
    longitude,
    efficiency,
    azimuth,
    slope,
    module_power=0.5,
    system_losses=15
):
    """
    Calls the PVGIS API and returns the result in JSON format
    filtering only the 'time' and 'P' fields from hourly data.

    IMPORTANT! in the end of the json output there are some explanatory notes
    about the data, remove them if it causes issues in your application.
    """
    url = "https://re.jrc.ec.europa.eu/api/seriescalc"
    params = {
        "lat": latitude,
        "lon": longitude,
        "outputformat": "json",
        "pvcalculation": "1",
        "peakpower": module_power,
        "angle": int(slope),
        "aspect": int(azimuth),
        "efficiency": efficiency,
        "raddatabase": "PVGIS-ERA5",
        "startyear": "2023",
        "endyear": "2023",
        "timeseries": "1",
        "mountingplace": "free",
        "loss": system_losses
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            
            # Remove meta explanatory fields
            if 'meta' in data:
                del data['meta']
                
            # Filter hourly data keeping only 'time' and 'P'
            if 'outputs' in data and 'hourly' in data['outputs']:
                data['outputs']['hourly'] = [
                    {'time': record['time'], 'P(kW)': record['P']} 
                    for record in data['outputs']['hourly']
                ]
            return data
        except ValueError:
            return {"error": "Error in JSON response decoding"}
    else:
        try:
            return {"error": response.json()}
        except ValueError:
            return {"error": response.text}