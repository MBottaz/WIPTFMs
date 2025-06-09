import pandas as pd

def convert_output_pvgis_to_dataframe(output_json):
    """
    Converte l'output JSON di PVGIS in un DataFrame pandas.
    """
    try:
        timeseries = output_json["outputs"]["hourly"]
        df = pd.DataFrame(timeseries)
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
        return df
    except (KeyError, ValueError) as e:
        print("Errore nella conversione:", e)
        return None