import requests
import json
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

def process_csv(file_paths):
    """
    Legge una lista di file CSV, li concatena, calcola le somme delle colonne specificate e crea un DataFrame.

    Args:
        file_paths (list): Una lista di percorsi di file CSV.

    Returns:
        pandas.DataFrame: Il DataFrame risultante.
    """

    # Leggi e concatena i file CSV
    dfs = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path, sep=";", header=0)
            dfs.append(df)
        except FileNotFoundError:
            print(f"File non trovato: {file_path}")
            return None

    if not dfs:
        print("Nessun file valido trovato.")
        return None

    combined_df = pd.concat(dfs, ignore_index=False)
    combined_df = combined_df.reset_index(drop=False)

    # Crea un nuovo DataFrame con la prima colonna
    new_df = pd.DataFrame(combined_df.iloc[:, 0].copy())

    # Itera sulle colonne per calcolare le somme e aggiungerle al nuovo DataFrame
    for i in range(1, len(combined_df.columns) - 3, 4):
        # col_name = f"{combined_df.columns[i+1][:5]}-{combined_df.columns[i+4][-5:]}"
        col_name = int(f"{combined_df.columns[i+1][:2]}")
        new_df[col_name] = combined_df.iloc[:, i:i+4].apply(lambda row: sum(map(lambda x: float(str(x).replace(",", ".")), row)), axis=1)

    print(new_df)
    # new_df = new_df.drop('Giorno', axis=1)

    return new_df

def trasforma_dataframe(df):
    """
    Trasforma un DataFrame con una colonna 'time' e colonne di dati orarie in un DataFrame
    con date come righe e ore come colonne, con una terza dimensione per i dati.

    Args:
        df (pd.DataFrame): DataFrame di input con una colonna 'time' e colonne di dati orarie.

    Returns:
        pd.DataFrame: DataFrame trasformato, o None se 'time' non esiste.
    """

    
    # Estrai i nomi delle colonne dei dati
    data_cols = [col for col in df.columns if col != 'time']

    # Estrai le date e le ore dalla colonna 'time'
    df['time'] = pd.to_datetime(df['time'])
    df['date'] = df['time'].dt.date
    df['hour'] = df['time'].dt.hour

    # Crea un DataFrame vuoto per i risultati
    dates = df['date'].unique()
    hours = sorted(df['hour'].unique())
    result = pd.DataFrame(index=dates, columns=pd.MultiIndex.from_product([hours, data_cols]))

    # Popola il DataFrame dei risultati
    for date in dates:
        for hour in hours:
            for col in data_cols:
                value = df.loc[(df['date'] == date) & (df['hour'] == hour), col].values
                if len(value) > 0:
                    result.loc[date, (hour, col)] = value[0]
                else:
                    result.loc[date, (hour, col)] = None
                    
    result=result.reset_index()

    return result

def somma_colonne_per_ora(df, colonne_da_sommare):
    """
    Somma le colonne specificate per ogni fascia oraria in un DataFrame con MultiIndex.

    Args:
        df (pd.DataFrame): Il DataFrame di input con MultiIndex per le colonne.
        colonne_da_sommare (list): Una lista di stringhe che rappresentano i nomi delle colonne da sommare.

    Returns:
        pd.DataFrame: Un nuovo DataFrame contenente la somma delle colonne specificate per ogni ora.
    """

    # Estrai le ore dal MultiIndex
    ore = df.columns.levels[0]

    # Crea un DataFrame vuoto per i risultati
    risultati = pd.DataFrame(index=df.index, columns=ore)

    # Calcola la somma per ogni ora
    for ora in ore:
        colonne_ora = [(ora, col) for col in colonne_da_sommare]
        if all(col in df.columns for col in colonne_ora):  # Verifica se tutte le colonne esistono
            risultati[ora] = df[colonne_ora].sum(axis=1)
        else:
            print(f"Attenzione: alcune colonne per l'ora {ora} non esistono.")
            risultati[ora] = 0  # o pd.NA, a seconda di come vuoi gestire i valori mancanti

    return risultati

def calculate_pv_module_output(latitude, longitude, efficiency, azimuth, slope, module_power=0.5, system_losses=15, save_output="N"):

    # Parameters:
    # latitude (float): Latitude of the location (degrees)
    # longitude (float): Longitude of the location (degrees)
    # efficiency (float): Efficiency of the PV system after losses (percentage between 0 and 1)
    # azimuth (float): Azimuth angle of the panels in degrees (0° = south, 90° = west, 180° = north, 270° = east)
    # slope (float): Tilt angle of the panels in degrees (0° = horizontal, 90° = vertical)
    # module_power (float): Rated power of the PV module in kW (default is 0.5 kW)
    # system_losses (float): Total system losses as a percentage (default is 15%)
    # save_output (str): Option to save output as JSON ("Y" for yes, "N" for no, default is "N")

    # The output DataFrame contains the following columns:
    # 1. time: Timestamp of the data point (format: YYYYMMDD:HHMM)
    # 2. P: AC power output (kW) - The total electrical power generated by the PV system.
    # 3. G(i): In-plane irradiance (W/m²) - Solar radiation incident on the surface of the panel.
    # 4. H_sun: Sun height angle (°) - The angle of the sun relative to the horizon.
    # 5. T2m: Air temperature (°C) - Temperature of the air 2 meters above the ground.
    # 6. WS10m: Wind speed at 10 meters (m/s) - Wind speed measured 10 meters above the ground.
    # 7. Int: Irradiance intensity (W/m²) - Intensity of sunlight reaching the surface (could include direct and diffuse irradiance).

    
    # PVGIS API endpoint
    url = "https://re.jrc.ec.europa.eu/api/seriescalc"

    # Define API call parameters
    params = {
        "lat": latitude,  # Latitude of the location
        "lon": longitude,  # Longitude of the location
        "outputformat": "json",  # Output format: JSON
        "pvcalculation": "1",  # PV system calculation mode
        "peakpower": module_power,  # Rated power of the PV module/system in kW
        "angle": int(slope),  # Tilt angle of the PV panels in degrees
        "aspect": int(azimuth),  # Azimuth angle of the PV panels in degrees
        "efficiency": efficiency,  # Efficiency of the system after losses
        "raddatabase": "PVGIS-ERA5",  # Solar radiation database used
        "startyear": "2023",  # Start year for the data (valid range 2005-2023)
        "endyear": "2023",  # End year for the data (valid range 2005-2023)
        "timeseries": "1",  # Request for hourly output data
        "mountingplace": "free",  # Mounting place type: "free" for free-standing panels
        "loss": system_losses  # Total system losses (e.g., 15% losses)
    }

    # Send the API request to the PVGIS service
    response = requests.get(url, params=params)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        try:
            # Parse the JSON response from the PVGIS API
            data = response.json()

            # Extract hourly timeseries data and convert to DataFrame
            timeseries = data["outputs"]["hourly"]
            df = pd.DataFrame(timeseries)
            # Convert time from string to datetime format for easier manipulation
            df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")

            # Optionally save the JSON response to a local file
            if save_output.upper() == "Y":
                with open("energy_production.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("JSON file with energy production has been saved as 'energy_production.json'.")
            
            # print("Data processing complete!")
            return df
        except ValueError:
            # Handle potential errors when parsing the JSON data
            print("Error decoding the response data.")
            return None
    else:
        # If the API request fails, handle the error and print details
        try:
            # Attempt to parse JSON error response for more information
            error_info = response.json()
            print(f"Error details: {error_info}")
        except ValueError:
            # If the error response is not JSON, print the raw response text
            print(f"Error: {response.text}")
        
        return None

def process_multiple_pv_configurations(latitude, longitude, efficiency, *triplets):
    """
    Calculate PV module outputs for multiple configurations and return a DataFrame.
    
    Parameters:
    - latitude (float): Latitude of the location
    - longitude (float): Longitude of the location
    - efficiency (float): Efficiency of the system (0 to 1)
    - *triplets: Each triplet represents (slope, azimuth, PV power) for different configurations.
    
    Returns:
    - pd.DataFrame: DataFrame containing timestamp and "P" values for each configuration.
    """
    
    # Initialize an empty DataFrame to store the results
    final_df = pd.DataFrame()
    
    # Loop over each triplet of (slope, azimuth, module_power)
    for slope, azimuth, module_power in triplets:
        # Call the calculate_pv_module_output function for the current configuration
        df = calculate_pv_module_output(latitude, longitude, efficiency, azimuth, slope, module_power)
        
        if df is not None:
            # Extract the "P" column from the returned DataFrame
            p_column = df["P"]/1000
            
            # If final_df is empty, initialize it with the "time" column from the first configuration
            if final_df.empty:
                final_df["time"] = df["time"]
            
            # Add the "P" column for this configuration to the final DataFrame
            final_df[f"P_{slope}_{azimuth}_{module_power}"] = p_column
    
    final_df = trasforma_dataframe(final_df)
    
    # Return the final Da
    return final_df
    
def controlla_e_allinea_dataframe(df1, df2):
    """
    Verifica se due DataFrame hanno lo stesso numero di righe e allinea il DataFrame
    più lungo rimuovendo le righe in eccesso.

    Args:
        df1 (pd.DataFrame): Il primo DataFrame.
        df2 (pd.DataFrame): Il secondo DataFrame.

    Returns:
        tuple: Una tupla contenente i due DataFrame allineati.
    """

    print("Tail di df1 prima dell'allineamento:")
    print(df1.tail())
    print("\nTail di df2 prima dell'allineamento:")
    print(df2.tail())

    if len(df1) != len(df2):
        min_len = min(len(df1), len(df2))
        df1_allineato = df1.iloc[:min_len]
        df2_allineato = df2.iloc[:min_len]

        print("\nDataFrame allineati. Righe rimosse dal DataFrame più lungo.")
    else:
        df1_allineato = df1.copy()
        df2_allineato = df2.copy()
        print("\nI DataFrame hanno lo stesso numero di righe. Nessuna rimozione necessaria.")

    print("\nTail di df1 dopo l'allineamento:")
    print(df1_allineato.tail())
    print("\nTail di df2 dopo l'allineamento:")
    print(df2_allineato.tail())

    return df1_allineato, df2_allineato

def sottrai_dataframes(df1, df2):
    # Assicurati che entrambi i DataFrame abbiano lo stesso indice
    if not df1.index.equals(df2.index):
        raise ValueError("I DataFrame devono avere lo stesso indice.")
    
    # Separare le colonne numeriche (escludendo gli indici)
    df1_numeric = df1.drop('index', axis=1, inplace=False)  # Creiamo una copia per lavorare solo sulle colonne numeriche
    df2_numeric = df2.drop('index', axis=1, inplace=False)  # Creiamo una copia anche qui
    
    df1_numeric = df1_numeric.applymap(pd.to_numeric, errors='coerce')
    df2_numeric = df2_numeric.applymap(pd.to_numeric, errors='coerce')

    # Eseguiamo la sottrazione solo sulle colonne numeriche
    df_differenza_numeric = df1_numeric - df2_numeric

    return df_differenza_numeric

def plot_heatmap(df):
    """
    Funzione per generare una heatmap da un DataFrame.
    
    Parametri:
    df : pandas.DataFrame
        Il DataFrame con i dati numerici da visualizzare.
    """
    # Impostare la dimensione della figura
    plt.figure(figsize=(10, 8))
    
    # Creare la heatmap con una scala di colori personalizzata
    sns.heatmap(df, cmap='coolwarm', annot=False, fmt='.2f', cbar=True, vmin=-6, vmax=6)
    
    # Aggiungere etichette e titolo
    plt.title('Heatmap del DataFrame')
    plt.xlabel('Colonne')
    plt.ylabel('Indici temporali')
    
    # Mostrare la heatmap
    plt.show()

# ------------------main ------------- 

# Example usage
latitude = 44.516  # Provided latitude
longitude = 11.518  # Provided longitude
efficiency = 0.23  # 23% efficiency

PV_subsets = [
    (35, 23, 0.47),  # Slope, Azimuth, PV Power
    (35, -157, 0.47),  # Slope, Azimuth, PV Power
    (35, 113, 0.47)   # Slope, Azimuth, PV Power
]

"""
# ------- DEBUG ------
azimuth = 23  # azimuth angle in degrees (0 = South, 90 = West, -90 = East, 180 = North)
slope = 35  # 35 degree tilt
PV_power = 0.47  # Peak power in kW (e.g., 300W = 0.3kW)
# ----------------------
"""

df = process_multiple_pv_configurations(latitude, longitude, efficiency, *PV_subsets)

colonne_da_sommare = ['P_35_23_0.47', 'P_35_-157_0.47', 'P_35_113_0.47']
df_somma = somma_colonne_per_ora(df, colonne_da_sommare)

"""
# ------- DEBUG ------
if isinstance(df, pd.DataFrame):
    print(df.head())
else:
    print("Returned value is not a DataFrame.")
# ----------------------
"""

# input_directory = '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_gennaio.csv'


input_directory = ['/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_gennaio.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_febbraio.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_marzo.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_aprile.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_maggio.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_giugno.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_luglio.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_agosto.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_settembre.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_ottobre.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_novembre.csv',
               '/home/santa/Documenti/Energia/WIPTFMs/data/ExportData_dicembre.csv']

consumption_df = process_csv(input_directory)

df_somma_a, consumption_df_a = controlla_e_allinea_dataframe(df_somma, consumption_df)


df_differenza = sottrai_dataframes(df_somma_a, consumption_df_a)
df_differenza['index'] = consumption_df_a['index']
df_differenza=df_differenza.set_index('index')

plot_heatmap(df_differenza)
