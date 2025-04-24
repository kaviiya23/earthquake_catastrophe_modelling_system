"""
Utility functions for the Earthquake Risk Assessment App
"""

import pandas as pd
import numpy as np
import os

def load_data(file_path):
    """
    Load and preprocess earthquake risk dataset
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    
    Returns:
    --------
    pandas DataFrame
        Preprocessed DataFrame
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Ensure required columns exist
    required_columns = [
        'City', 'Frequency_Past_EQ', 'Average_Magnitude', 
        'Time_Since_Last_Event', 'Nearby_Fault_Activity'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        # Create missing columns with default values
        for col in missing_columns:
            if col == 'City':
                df['City'] = [f'City_{i}' for i in range(len(df))]
            elif col == 'Frequency_Past_EQ':
                df['Frequency_Past_EQ'] = np.random.randint(1, 10, len(df))
            elif col == 'Average_Magnitude':
                df['Average_Magnitude'] = np.random.uniform(4.0, 7.5, len(df)).round(1)
            elif col == 'Time_Since_Last_Event':
                df['Time_Since_Last_Event'] = np.random.randint(1, 20, len(df))
            elif col == 'Nearby_Fault_Activity':
                df['Nearby_Fault_Activity'] = np.random.choice(['Low', 'Medium', 'High'], len(df))
    
    # Add Depth_km if missing
    if 'Depth_km' not in df.columns:
        df['Depth_km'] = np.random.randint(5, 30, len(df))
    
    # Add Soil_Type if missing
    if 'Soil_Type' not in df.columns:
        df['Soil_Type'] = np.random.choice(['Rock', 'Stiff', 'Soft', 'Very Soft'], len(df))
    
    # Convert columns to appropriate types
    df['Frequency_Past_EQ'] = pd.to_numeric(df['Frequency_Past_EQ'], errors='coerce').fillna(0)
    df['Average_Magnitude'] = pd.to_numeric(df['Average_Magnitude'], errors='coerce').fillna(5.0)
    df['Time_Since_Last_Event'] = pd.to_numeric(df['Time_Since_Last_Event'], errors='coerce').fillna(5)
    df['Depth_km'] = pd.to_numeric(df['Depth_km'], errors='coerce').fillna(10)
    
    return df

def format_currency(amount, currency="₹"):
    """
    Format a number as currency
    
    Parameters:
    -----------
    amount : float
        Amount to format
    currency : str, optional
        Currency symbol, by default "₹"
    
    Returns:
    --------
    str
        Formatted currency string
    """
    try:
        # Convert to float and round
        value = float(amount)
        
        # Format based on value scale
        if value >= 10000000:  # 1 crore or more
            return f"{currency}{value/10000000:.2f} Crore"
        elif value >= 100000:  # 1 lakh or more
            return f"{currency}{value/100000:.2f} Lakh"
        elif value >= 1000:  # 1 thousand or more
            return f"{currency}{value/1000:.2f}K"
        else:
            return f"{currency}{value:.2f}"
    except:
        return f"{currency}0.00"

def get_scenario_multiplier(scenario):
    """
    Get modifier multiplier based on scenario type
    
    Parameters:
    -----------
    scenario : str
        Scenario type ('Best Case', 'Expected Case', 'Worst Case')
    
    Returns:
    --------
    float
        Multiplier for scenario calculations
    """
    multipliers = {
        'Best Case': 0.7,
        'Expected Case': 1.0,
        'Worst Case': 1.5
    }
    
    return multipliers.get(scenario, 1.0)

def create_init_file():
    """
    Create __init__.py file for modules package
    """
    init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
    
    # Only create if it doesn't exist
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('# Earthquake Risk Assessment Modules\n')