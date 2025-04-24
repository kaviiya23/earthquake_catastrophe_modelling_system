"""
Financial Module: Calculates economic impact of earthquake damage
"""

import pandas as pd
import numpy as np

def estimate_building_value(building_type, building_size_sqft):
    """
    Estimate building value based on type and size
    
    Parameters:
    -----------
    building_type : str
        Type of building
    building_size_sqft : float
        Building size in square feet
    
    Returns:
    --------
    float
        Estimated building value in INR
    """
    # Base rate per sq ft by building type (in INR)
    base_rates = {
        'Residential': 2000,
        'Commercial': 3500,
        'High-rise': 4000,
        'School': 3000,
        'Hospital': 5000,
        'Industrial': 2500
    }
    
    # Get base rate, default to residential if type not found
    base_rate = base_rates.get(building_type, 2000)
    
    # Calculate estimated value
    estimated_value = base_rate * building_size_sqft
    
    # Apply minimum value based on building type
    min_values = {
        'Residential': 1000000,      # 10 Lakh
        'Commercial': 2500000,       # 25 Lakh
        'High-rise': 10000000,       # 1 Crore
        'School': 5000000,           # 50 Lakh
        'Hospital': 10000000,        # 1 Crore
        'Industrial': 5000000        # 50 Lakh
    }
    
    # Ensure value is at least the minimum for the building type
    min_value = min_values.get(building_type, 1000000)
    estimated_value = max(estimated_value, min_value)
    
    return estimated_value

def calculate_financial_impact(data):
    """
    Calculate financial impact of earthquake damage
    
    Parameters:
    -----------
    data : dict or pandas Series
        A dictionary or Series containing:
        - Damage_Percent: Estimated damage percentage
        - Building_Value: Value of building in INR
        - Num_Structures: Number of affected structures
        - Insurance_Coverage: Insurance coverage ratio (0-1)
    
    Returns:
    --------
    tuple
        (total_loss, insurance_recovery, net_loss)
    """
    try:
        # Extract data
        damage_percent = float(data.get('Damage_Percent', 0))
        building_value = float(data.get('Building_Value', 0))
        num_structures = int(data.get('Num_Structures', 1))
        insurance_coverage = float(data.get('Insurance_Coverage', 0))
        
        # Calculate loss per structure
        loss_per_structure = building_value * (damage_percent / 100)
        
        # Calculate total loss
        total_loss = loss_per_structure * num_structures
        
        # Calculate insurance recovery
        insurance_recovery = total_loss * insurance_coverage
        
        # Calculate net loss
        net_loss = total_loss - insurance_recovery
        
        return round(total_loss), round(insurance_recovery), round(net_loss)
    
    except (ValueError, TypeError) as e:
        # Return default values if calculation fails
        print(f"Financial calculation error: {e}")
        return 0, 0, 0

def calculate_recovery_timeline(total_loss, recovery_months=24):
    """
    Calculate expected recovery costs over time
    
    Parameters:
    -----------
    total_loss : float
        Total economic loss
    recovery_months : int
        Expected recovery period in months
    
    Returns:
    --------
    pandas DataFrame
        DataFrame with monthly and cumulative recovery costs
    """
    recovery_data = []
    
    for month in range(recovery_months + 1):
        if month == 0:
            cumulative_cost = 0
        else:
            # Recovery follows a logarithmic pattern
            recovery_percentage = min(100, 30 * np.log10(month + 1))
            cumulative_cost = total_loss * (recovery_percentage / 100)
        
        # Calculate monthly cost
        previous_cost = 0 if month == 0 else recovery_data[month-1]['cumulative_cost']
        monthly_cost = cumulative_cost - previous_cost
        
        recovery_data.append({
            'month': month,
            'monthly_cost': monthly_cost,
            'cumulative_cost': cumulative_cost
        })
    
    return pd.DataFrame(recovery_data)