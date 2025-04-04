import requests

def calculate_pv_module_output(latitude, longitude, efficiency, azimuth, slope, module_power=0.3, system_losses=15):
    # Assumed system losses (total losses due to inverter, wiring, shading, etc.)
    # The loss value should be a percentage (e.g., 15 means 15% system loss)
    
    # PVGIS API endpoint
    url = "https://re.jrc.ec.europa.eu/api/seriescalc"

    # Parameters for the API call
    params = {
        "lat": latitude,  # Latitude of the location (degrees)
        "lon": longitude,  # Longitude of the location (degrees)
        "outputformat": "csv",  # Specify CSV output format
        "pvcalculation": "1",  # Set to 1 for PV system calculation
        "peakpower": module_power,  # Rated power of the module/system in kW (e.g., 0.3 for 300W module)
        "tilt": slope,  # Tilt of the panels in degrees
        "azimuth": azimuth,  # Azimuth angle of the panels
        "efficiency": efficiency,  # Efficiency after losses
        "raddatabase": "PVGIS-ERA5",  # Solar radiation database
        "startyear": "2023",  # Start year (valid range 2005-2023)
        "endyear": "2023",  # End year (valid range 2005-2023)
        "timeseries": "1",  # Request hourly output
        "loss": system_losses  # Total system losses (e.g., 15% losses)
    }

    # Send the request to PVGIS
    response = requests.get(url, params=params)

    # Debugging: print the status code and response content for further troubleshooting
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        # Save the CSV file returned by PVGIS API
        with open("energy_production.csv", "wb") as f:
            f.write(response.content)
        
        print("CSV file with energy production has been saved as 'energy_production.csv'.")
        return "energy_production.csv"
    else:
        # If status code is not 200, print out the detailed error information.
        try:
            # Try to parse JSON error response (if available)
            error_info = response.json()
            print(f"Error details: {error_info}")
        except ValueError:
            # If no JSON response, print raw content
            print(f"Error: {response.text}")
        
        return None

# Example usage
latitude = 44.516  # Provided latitude
longitude = 11.518  # Provided longitude
efficiency = 0.23  # 23% efficiency
azimuth = 23  # Slightly east of south
slope = 35  # 35 degree tilt
system_losses = 15  # Assuming 15% system losses (inverter, shading, etc.)
module_power = 0.47  # Peak power of a single PV module (e.g., 300W = 0.3kW)

calculate_pv_module_output(latitude, longitude, efficiency, azimuth, slope, system_losses=system_losses, module_power=module_power)
