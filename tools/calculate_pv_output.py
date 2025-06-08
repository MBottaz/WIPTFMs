import requests
import json

def calculate_pv_output(
    latitude: float,
    longitude: float,
    efficiency: float,
    azimuth: float,
    slope: float,
    module_power: float = 0.5,
    system_losses: float = 15.0,
    year: int = 2023,
    save_output: bool = False
) -> dict:
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
        "startyear": str(year),
        "endyear": str(year),
        "timeseries": "1",
        "mountingplace": "free",
        "loss": system_losses
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if save_output:
            with open("data/energy_production.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        summary = data.get("outputs", {}).get("totals", {}).get(str(year), {})
        return {
            "location": data.get("meta", {}).get("location", {}),
            "year": year,
            "summary": summary
        }

    else:
        return {"error": f"Errore nella richiesta: {response.status_code}"}