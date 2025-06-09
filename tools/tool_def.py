# tool_def.py

from langchain.tools import tool
from tools.pv_output_estimator import pv_output

@tool
def estimate_pv_output_tool(
    latitude: float,
    longitude: float,
    efficiency: float,
    azimuth: float,
    tilt: float,
    module_power: float = 0.5,
    system_losses: float = 15,
) -> float:
    """
    Estimate annual photovoltaic (PV) system energy production.
    
    This tool calculates the total annual energy output of a solar PV system
    based on location and system parameters.
    
    Args:
        latitude (float): Geographic latitude in decimal degrees (-90 to 90)
        longitude (float): Geographic longitude in decimal degrees (-180 to 180)
        efficiency (float): Overall system efficiency as decimal (0.0 to 1.0, e.g., 0.85 for 85%)
        azimuth (float): Panel azimuth angle in degrees (0° = south, 90° = west, 180° = north, 270° = east)
        tilt (float): Panel tilt angle in degrees (0° = horizontal, 90° = vertical)
        module_power (float, optional): Rated power of solar module in kW. Defaults to 0.5
        system_losses (float, optional): Total system losses as percentage. Defaults to 15
    
    Returns:
        float: Annual energy production in kWh
    """
    # Get raw calculation data
    raw_data = pv_output(
        latitude,
        longitude,
        efficiency,
        azimuth,
        tilt,
        module_power,
        system_losses
    )
    
    # Calculate annual production
    if isinstance(raw_data, dict):
        hourly_outputs = raw_data.get('hourly_output', [])
        if hourly_outputs:
            daily_total = sum(hourly_outputs)
            annual_production = daily_total * 365
        else:
            annual_production = 0
    else:
        annual_production = 0
    
    return annual_production
