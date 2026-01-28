"""
Enhanced CSV Reader MCP Server with Aggregation (FastMCP)

Example prompts to test this server:
what are the total units sold by product in the sample CSV?
/read_csv file_path="/path/to/your/data.csv"
/aggregate_csv file_path="sample.csv" group_by="Category" agg_column="Sales_Amount" agg_function="sum"
/aggregate_csv file_path="sample.csv" group_by="Region,Customer_Type" agg_column="Units_Sold" agg_function="mean"
"""

# For reading and analyzing CSV files
import pandas as pd
# For file path handling
from pathlib import Path
# FastMCP for simplified MCP server creation
from fastmcp import FastMCP
# Asynchronous support
import asyncio

from library.Consumption import load_csv, reprocess_csv_edistribuzione
from library.PV import calculate_pv_module_output

# Create a new FastMCP server instance
mcp = FastMCP("csv-reader-server")

@mcp.tool()
def read_csv(file_path: str) -> str:
    """
    Reads a CSV file and returns its contents and basic info.
    
    Use when: analyzing data files, checking CSV structure, or viewing data samples.
    Examples: 'read sales.csv', 'analyze the data file', 'show me what's in the CSV'
    
    Args:
        file_path: Path to the CSV file to read. Can be absolute or relative.
    
    Returns:
        String containing file info and preview of the data.
    """
    try:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return f"Error: File not found at {file_path_obj}"
        
        # Read the CSV file into a dataframe
        df = pd.read_csv(file_path_obj)
        
        # Build result message with file info
        result = f"Successfully read CSV: {file_path_obj}\n"
        result += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        result += f"Columns: {', '.join(df.columns)}\n\n"
        
        # Add first 5 rows as preview
        result += "First 5 rows:\n"
        result += df.head().to_string()

        result += "Last 5 rows:\n"
        result += df.tail().to_string()
        
        return result
        
    except Exception as e:
        return f"Error reading CSV: {str(e)}"
    

@mcp.tool()
def aggregate_csv(input_file_folder: str) -> str:
    """
    Aggregates and reprocesses CSV data from e-distribuzione format.
    
    This tool loads a CSV file, applies e-distribuzione-specific transformations,
    and saves the processed output to 'data/output.csv'. It returns a preview
    of the results including the first and last 5 rows.
    
    Args:
        input_file_folder: Folder containing the CSV input file.
                           Should point to a valid e-distribuzione formatted CSV file.
    
    Returns:
        A string containing:
        - Success/error message
        - Preview of first 5 rows (if successful)
        - Preview of last 5 rows (if successful)
    
    Output:
        - Writes processed CSV to: data/output.csv
        - Output file will overwrite existing file if present
    
    Example:
        aggregate_csv("input")
    
    Note:
        This tool is specifically designed for e-distribuzione CSV format.
        Using it with other CSV formats may produce unexpected results.
    """
    
    output_file_folder = 'data'

    try:
        df = load_csv(input_file_folder)
        df = reprocess_csv_edistribuzione(df)

        df.to_csv(output_file_folder+'/output.csv', index=False)

        result = "Successfully aggregated CSV, saved in: {output_file_folder}\n"

        # Add first 5 rows as preview
        result += "First 5 rows:\n"
        result += df.head().to_string()

        result += "Last 5 rows:\n"
        result += df.tail().to_string()

        return result

    except Exception as e:
        return f"Error processing CSV: {str(e)}"

@mcp.tool()
def calculate_pv_output(latitude: float, longitude: float, efficiency: float, slope: float, azimuth: float, module_power: float) -> str:
    """
    Calculate PV module output for a given configuration and return a DataFrame preview.
    
    Parameters:
    - latitude (float): Latitude of the location
    - longitude (float): Longitude of the location
    - efficiency (float): Efficiency of the system (0 to 1), you can assume 0.23 which is the average efficiency of state of the art PV modules
    - slope (float): Slope angle of the PV module, (choose one between 15 degrees for low-tilt roofs, and 30 degrees for optimal tilt installation)
    - azimuth (float): Azimuth angle of the PV module (0° = south, 90° = west, 180° = north, 270° = east, it can be also values in between)
    - module_power (float): Peak power of the PV module in kW (e.g., 0.3 for 300W). Perform the calculation for a single module.
    
    Returns:
    - str: Preview of the resulting DataFrame with timestamp and "P" values.
    """
    
    df = calculate_pv_module_output(latitude, longitude, efficiency, azimuth, slope, module_power)
    
    if df is not None:
        result = f"PV Output Calculation Result:\n"
        result += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        result += f"Columns: {', '.join(df.columns)}\n\n"
        
        # Add first 5 rows as preview
        result += "First 5 rows:\n"
        result += df.head().to_string()

        result += "\nLast 5 rows:\n"
        result += df.tail().to_string()
        
        return result
    else:
        return "Error calculating PV output."   

    
# Run the server when script is executed directly
if __name__ == "__main__":
    mcp.run()