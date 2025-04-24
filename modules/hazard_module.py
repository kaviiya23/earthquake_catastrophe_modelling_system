"""
Hazard Module: Estimates severity if an earthquake occurs
"""

import pandas as pd
import numpy as np

def calculate_hazard_score(row):
    """
    Calculate hazard score based on earthquake parameters
    
    Parameters:
    -----------
    row : dict or pandas Series
        A dictionary or Series containing the following keys:
        - Average_Magnitude: Average magnitude of earthquakes in the area
        - Depth_km: Average depth of earthquakes in km
        - Nearby_Fault_Activity: Qualitative assessment of fault activity ('Low', 'Medium', 'High')
        - Soil_Type: (Optional) Type of soil in the area
    
    Returns:
    --------
    float
        Hazard score on a 0-10 scale
    """
    try:
        # Ensure numeric values
        avg_magnitude = float(row.get('Average_Magnitude', 0))
        depth_km = float(row.get('Depth_km', 10))  # Default to 10km if missing
        
        # Convert fault activity to numeric
        fault_activity_map = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
        fault_activity = fault_activity_map.get(row.get('Nearby_Fault_Activity', 'Low'), 0.3)
        
        # Include soil amplification if available
        soil_amplification_map = {
            'Rock': 0.8,
            'Stiff': 1.0,
            'Soft': 1.3,
            'Very Soft': 1.6
        }
        soil_factor = soil_amplification_map.get(row.get('Soil_Type', 'Stiff'), 1.0)
        
        # Calculate hazard components
        magnitude_component = avg_magnitude * 0.7  # Scale magnitude impact (typically 4-8)
        depth_component = (15 / (depth_km + 5)) * 2  # Inverse depth impact (shallow = higher hazard)
        fault_component = fault_activity * 3  # Fault activity impact
        
        # Calculate the final score with soil amplification
        hazard_score = (magnitude_component + depth_component + fault_component) * soil_factor
        
        # Normalize to 0-10 scale
        hazard_score = min(10, max(0, hazard_score))
        
        return round(hazard_score, 2)
    
    except (ValueError, TypeError):
        # Return a default score if calculation fails
        return 5.0  # Mid-range default

def categorize_hazard_level(hazard_score):
    """
    Categorize hazard score into qualitative hazard level
    
    Parameters:
    -----------
    hazard_score : float
        Hazard score on a 0-10 scale
    
    Returns:
    --------
    str
        Qualitative hazard level ('Low', 'Moderate', 'High', or 'Very High')
    """
    try:
        score = float(hazard_score)
        
        if score < 3.5:
            return "Low"
        elif score < 6.0:
            return "Moderate"
        elif score < 8.0:
            return "High"
        else:
            return "Very High"
    except:
        return "Moderate"  # Default if conversion fails