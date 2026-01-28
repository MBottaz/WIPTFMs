import os
import pandas as pd
from datetime import datetime
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def load_csv(folder):
    """
    Load all the CSVs in the specified folder and concatenate them into a single DataFrame.

    """
    try:
        filepaths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.csv')]
        df = pd.concat(map(lambda f: pd.read_csv(f, sep=';', index_col=False, decimal=','), filepaths), ignore_index=True)
    except FileNotFoundError:
        print(f"File non trovato: {folder}")
        return None

    return df

def reprocess_csv_edistribuzione(df):
    """
    Reprocess the CSV from E-Distribuzione to have a DataFrame with hourly profile.

    Args:
        df (pandas.DataFrame): DataFrame obtained from edistribuzione CSV, with the following structure (unit measure is kWh):
        
            | timestamp  | 00:00-06:00 | 06:00-12:00 | 12:00-18:00 | 18:00-24:00 |
            |------------|-------------|-------------|-------------|-------------|
            | 2023-01-01 | 1,23        | 4,56        | 7,89        | 0,12        | 
            | 2023-01-02 | 2,34        | 5,67        | 8,90        | 1,23        | 
            | ...        | ...         | ...         | ...         | ...         | 

    Returns:
        pandas.DataFrame: Dataframe with everything in one column.
    """

# Identify time interval columns (all columns except the first one)
    time_cols = df.columns[1:].tolist()
    
    # Melt the dataframe to long format
    df_long = df.melt(
        id_vars=df.columns[0],
        value_vars=time_cols,
        var_name='time_interval',
        value_name='consumption'
    )
        
    # Extract start time from interval (e.g., "00:00-00:15" -> "00:00")
    df_long['time'] = df_long['time_interval'].apply(extract_start_time)

    # Combine date and time into a single timestamp
    df_long['timestamp'] = pd.to_datetime(
        df_long[df.columns[0]].astype(str) + ' ' + df_long['time'],
    format='%d/%m/%Y %H:%M'
    )

    # Select and sort final columns
    result = df_long[['timestamp', 'consumption']].sort_values('timestamp').reset_index(drop=True)


    return result

def extract_start_time(interval_str):
    """
    Extract the start time from various interval formats.
    Examples: "00:00-06:00" -> "00:00", "14:00" -> "14:00"
    """
    # Try to match time range format (e.g., "00:00-06:00")
    match = re.match(r'(\d{1,2}:\d{2})', str(interval_str))
    if match:
        return match.group(1)
    return interval_str


def create_output_file(input_directory='input', output_directory='data'):

    consumption_df = load_csv(input_directory)
    consumption_df = reprocess_csv_edistribuzione(consumption_df)

    consumption_df.to_csv(output_directory+'/output.csv', index=False)

    return None

def plot_gaussian_curve(data, label="Data", bins=20, figsize=(10, 6)):
    """
    Plots a histogram of the data with a fitted Gaussian curve overlay.
    
    Parameters:
    -----------
    data : array-like
        The data column to analyze (pandas Series, numpy array, or list)
    label : str
        Label for the plot title and legend
    bins : int
        Number of bins for the histogram
    figsize : tuple
        Figure size (width, height)
    
    Returns:
    --------
    dict : Contains fitted parameters (mean, std) and statistics
    """
    # Remove NaN values
    clean_data = np.array(data)
    clean_data = clean_data[~np.isnan(clean_data)]
    
    # Calculate statistics
    mean = np.mean(clean_data)
    std = np.std(clean_data)
    
    # Create figure
    plt.figure(figsize=figsize)
    
    # Plot histogram
    n, bins_edges, patches = plt.hist(clean_data, bins=bins, density=True, 
                                       alpha=0.7, color='skyblue', 
                                       edgecolor='black', label='Data distribution')
    
    # Generate Gaussian curve
    x = np.linspace(clean_data.min(), clean_data.max(), 1000)
    gaussian = stats.norm.pdf(x, mean, std)
    
    # Plot Gaussian curve
    plt.plot(x, gaussian, 'r-', linewidth=2, label=f'Gaussian fit\nμ={mean:.2f}, σ={std:.2f}')
    
    # Formatting
    plt.xlabel(label, fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.title(f'Gaussian Distribution - {label}', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Return statistics
    return {
        'mean': mean,
        'std': std,
        'n_samples': len(clean_data),
        'min': clean_data.min(),
        'max': clean_data.max()
    }


if __name__ == "__main__":

    df = load_csv('input')
    df = reprocess_csv_edistribuzione(df)
    df_daily = df.set_index('timestamp').resample('D').sum()
    print(df_daily.head())
    statistics = plot_gaussian_curve(df_daily['consumption'], label="Consumption (kWh)")
    