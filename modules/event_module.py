import numpy as np
import pandas as pd
from math import log
from sklearn.cluster import KMeans

def calculate_event_score(row, weight=1.5):
    """
    Calculate event score based on historical seismic activity
    
    Parameters:
    -----------
    row : dict or pandas Series
        A dictionary or Series containing the following keys:
        - Frequency_Past_EQ: Number of earthquakes in the past 10 years
        - Nearby_Fault_Activity: Qualitative assessment of fault activity ('Low', 'Medium', 'High')
        - Time_Since_Last_Event: Time since the last earthquake in years
    weight : float, optional
        Weight factor for fault activity, by default 1.5
    
    Returns:
    --------
    float
        Log-probability score indicating earthquake likelihood
    """
    # Convert text-based fault activity to numeric score
    activity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    
    # Get the activity score, defaulting to 1 if missing
    activity_score = activity_mapping.get(row['Nearby_Fault_Activity'], 1)
    
    # Calculate score using the formula:
    # log((frequency + weight * activity) / (time_since_last + 1))
    # Adding 1 to time_since_last to avoid division by zero
    try:
        frequency = float(row['Frequency_Past_EQ'])
        time_since_last = float(row['Time_Since_Last_Event'])
        
        # Calculate the score
        score = log((frequency + weight * activity_score) / (time_since_last + 1))
        return round(score, 4)
    except (ValueError, TypeError):
        # Return a default score if calculation fails
        return -1.0

def assign_event_risk_zone(df, n_clusters=3):
    """
    Divide regions into risk propensity zones using clustering
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame containing earthquake data for multiple cities
    n_clusters : int, optional
        Number of clusters for risk zones, by default 3
    
    Returns:
    --------
    pandas DataFrame
        DataFrame with added columns for Risk_Propensity_Score and Event_Zone
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Map text-based fault activity to numeric values
    activity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    
    # Create numeric columns for clustering
    result_df['Nearby_Fault_Activity_numeric'] = result_df['Nearby_Fault_Activity'].map(activity_mapping).fillna(1)
    
    # Ensure numeric columns
    numeric_columns = ['Frequency_Past_EQ', 'Average_Magnitude', 'Time_Since_Last_Event', 'Nearby_Fault_Activity_numeric']
    for col in numeric_columns:
        if col in result_df.columns:
            result_df[col] = pd.to_numeric(result_df[col], errors='coerce').fillna(0)
    
    # Calculate risk propensity score
    result_df['Risk_Propensity_Score'] = result_df.apply(calculate_event_score, axis=1)
    
    # Prepare features for clustering
    try:
        features = result_df[numeric_columns].values
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        result_df['Event_Zone'] = kmeans.fit_predict(features)
    except Exception as e:
        # If clustering fails, assign zones based on risk score
        print(f"KMeans clustering failed: {e}")
        result_df['Event_Zone'] = pd.qcut(result_df['Risk_Propensity_Score'], n_clusters, labels=False, duplicates='drop')
    
    return result_df
