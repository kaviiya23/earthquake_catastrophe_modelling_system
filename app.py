import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import modules
from event_module import calculate_event_score, assign_event_risk_zone
from hazard_module import calculate_hazard_score, categorize_hazard_level
from vulnerability_module import (
    get_material_factor, get_age_factor, get_density_factor, get_hazard_factor,
    calculate_vulnerability_score, categorize_damage_level
)
from financial_module import estimate_building_value, calculate_financial_impact
from utils import load_data, format_currency

# Set page configuration
st.set_page_config(
    page_title="Earthquake Risk Assessment",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E88E5;
        text-align: center;
    }

    .module-header {
        font-size: 1.5rem !important;
        background-color: #CFD8DC;  /* Soft gray-blue background */
        color: #212121;             /* Dark text */
        padding: 0.5rem;
        border-radius: 0.5rem;
    }

    .info-box {
        background-color: #E3F2FD;  /* Light blue */
        color: #0D47A1;             /* Navy blue text */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2196F3;  /* Blue accent */
    }

    .warning-box {
        background-color: #FFF8E1;  /* Light amber */
        color: #E65100;             /* Dark amber text */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #FFA000;  /* Amber accent */
    }

    .result-box {
        background-color: #E8F5E9;  /* Light green */
        color: #1B5E20;             /* Dark green text */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #43A047;  /* Green accent */
        margin: 1rem 0;
    }

    .stExpander {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)



import os
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count())  # Or set to a specific number you prefer
# Main app header
st.markdown("<h1 class='main-header'>🌍 Earthquake Catastrophe Modeling System</h1>", unsafe_allow_html=True)

# Load data
@st.cache_data
def get_data():
    try:
        # Try to load from data directory
        df = load_data(os.path.join("data", "japan_earthquake_risk_dataset.csv"))
    except FileNotFoundError:
        # If not found, create sample data
        st.warning("No dataset found. Creating sample data for demonstration.")
        
        # Create sample data
        cities = ["Tokyo", "Osaka", "Kyoto", "Sapporo", "Fukuoka", "Sendai", "Nagoya", "Yokohama"]
        sample_data = {
            "City": cities,
            "Frequency_Past_EQ": np.random.randint(1, 10, len(cities)),
            "Average_Magnitude": np.random.uniform(4.0, 7.5, len(cities)).round(1),
            "Time_Since_Last_Event": np.random.randint(1, 20, len(cities)),
            "Depth_km": np.random.randint(5, 30, len(cities)),
            "Nearby_Fault_Activity": np.random.choice(["Low", "Medium", "High"], len(cities)),
            "Soil_Type": np.random.choice(["Rock", "Stiff", "Soft", "Very Soft"], len(cities))
        }
        df = pd.DataFrame(sample_data)
        
    # Pre-process data
    df = assign_event_risk_zone(df)
    df["Hazard_Score"] = df.apply(calculate_hazard_score, axis=1)
    df["Hazard_Level"] = df["Hazard_Score"].apply(categorize_hazard_level)
    
    return df

# Load data
df = get_data()

# Sidebar navigation
st.sidebar.image("https://via.placeholder.com/150x150.png?text=Earthquake+Risk", width=150)
st.sidebar.title("Navigation")

# Create tabs for each module
tab_names = ["Event Module", "Hazard Module", "Vulnerability Module", "Financial Module"]
current_tab = st.sidebar.radio("Select Module:", tab_names)

# City selector in sidebar (shared across modules)
available_cities = sorted(df["City"].unique())
selected_city = st.sidebar.selectbox("Select City:", available_cities)

# Get city data
city_data = df[df["City"] == selected_city].iloc[0]

# Current year
current_year = datetime.now().year

# Sidebar info
with st.sidebar.expander("About This App"):
    st.write("""
    This app provides a comprehensive earthquake risk assessment tool using a four-module approach:
    
    1. **Event Module**: Likelihood of earthquake occurrence
    2. **Hazard Module**: Potential severity if an earthquake occurs
    3. **Vulnerability Module**: Assessment of structural damage
    4. **Financial Module**: Economic impact estimation
    
    The app uses historical data and predictive modeling to provide risk assessments.
    """)

# EVENT MODULE
if current_tab == "Event Module":
    st.markdown("<h2 class='module-header'>🌍 EVENT MODULE: Earthquake Probability Assessment</h2>", unsafe_allow_html=True)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.subheader("Selected City Information")
        st.write(f"**City:** {selected_city}")
        st.write(f"**Historical Earthquake Frequency:** {city_data['Frequency_Past_EQ']} events in past 10 years")
        st.write(f"**Average Magnitude:** {city_data['Average_Magnitude']}")
        st.write(f"**Time Since Last Event:** {city_data['Time_Since_Last_Event']} years")
        st.write(f"**Nearby Fault Activity:** {city_data['Nearby_Fault_Activity']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        prediction_year = st.slider("Select Year for Prediction:", min_value=current_year, max_value=current_year + 50, value=current_year + 5)
        years_from_now = prediction_year - current_year
        
        # Calculate event score with modified time factor
        time_factor = max(1, city_data['Time_Since_Last_Event'] - years_from_now)
        event_score = calculate_event_score({
            'Frequency_Past_EQ': city_data['Frequency_Past_EQ'],
            'Nearby_Fault_Activity': city_data['Nearby_Fault_Activity'],
            'Time_Since_Last_Event': time_factor
        })
        
        # Calculate probability (normalize score to 0-100%)
        probability = min(90, max(5, (event_score + 3) * 20))  # Map typical scores (-3 to 2) to range 5-90%
        
        # Risk category
        if probability < 30:
            risk_level = "Low"
            risk_color = "green"
        elif probability < 60:
            risk_level = "Medium"
            risk_color = "orange"
        else:
            risk_level = "High"
            risk_color = "red"
    
    # Display results
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.subheader(f"Event Risk Analysis for {selected_city} in {prediction_year}")
    
    # Create probability gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Earthquake Probability"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': risk_color},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "lightyellow"},
                {'range': [60, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"**Risk Level:** {risk_level} ({probability:.1f}% probability)")
    st.write(f"**Event Score:** {event_score:.2f} (based on historical patterns and time projections)")
    
    st.info(f"Based on historical earthquake data for {selected_city}, there is a {probability:.1f}% probability of a significant earthquake occurring by {prediction_year}.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Historical comparison chart
    st.subheader("Regional Comparison")
    
    # Create comparison chart of cities by event score
    comparison_df = df.sort_values(by="Risk_Propensity_Score", ascending=False)
    
    fig = px.bar(
        comparison_df, 
        x="City", 
        y="Risk_Propensity_Score", 
        color="Nearby_Fault_Activity",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        },
        labels={"Risk_Propensity_Score": "Earthquake Risk Score", "City": ""},
        title="Earthquake Risk Comparison Across Cities"
    )
    
    # Highlight selected city
    fig.add_shape(
        type="rect",
        x0=comparison_df[comparison_df["City"] == selected_city].index[0] - 0.4,
        x1=comparison_df[comparison_df["City"] == selected_city].index[0] + 0.4,
        y0=0,
        y1=comparison_df[comparison_df["City"] == selected_city]["Risk_Propensity_Score"].values[0],
        line=dict(color="blue", width=3),
        fillcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
# HAZARD MODULE
elif current_tab == "Hazard Module":
    st.markdown("<h2 class='module-header'>🔥 HAZARD MODULE: Earthquake Severity Assessment</h2>", unsafe_allow_html=True)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.subheader("Selected City Information")
        st.write(f"**City:** {selected_city}")
        st.write(f"**Average Magnitude:** {city_data['Average_Magnitude']}")
        st.write(f"**Average Depth:** {city_data['Depth_km']} km")
        st.write(f"**Soil Type:** {city_data['Soil_Type']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Allow adjusting parameters with sliders (starting at historical values)
        adjusted_magnitude = st.slider(
            "Adjust Magnitude Estimate:", 
            min_value=4.0, 
            max_value=9.0, 
            value=float(city_data['Average_Magnitude']),
            step=0.1
        )
        
        adjusted_depth = st.slider(
            "Adjust Depth Estimate (km):", 
            min_value=1, 
            max_value=50, 
            value=int(city_data['Depth_km']),
            step=1
        )
        
        soil_options = ["Rock", "Stiff", "Soft", "Very Soft"]
        selected_soil = st.selectbox(
            "Soil Type:", 
            soil_options, 
            index=soil_options.index(city_data['Soil_Type']) if city_data['Soil_Type'] in soil_options else 0
        )
    
    # Calculate hazard score
    hazard_data = {
        'Average_Magnitude': adjusted_magnitude,
        'Depth_km': adjusted_depth,
        'Nearby_Fault_Activity': city_data['Nearby_Fault_Activity'],
        'Soil_Type': selected_soil
    }
    
    hazard_score = calculate_hazard_score(hazard_data)
    hazard_level = categorize_hazard_level(hazard_score)
    
    # Display hazard level
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.subheader(f"Hazard Assessment for {selected_city}")
    
    # Color-coded hazard level
    hazard_colors = {"Low": "green", "Moderate": "orange", "High": "red", "Very High": "darkred"}
    hazard_color = hazard_colors.get(hazard_level, "gray")
    
    # Create gauge chart for hazard score
    max_hazard_score = 10  # Maximum possible hazard score
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = hazard_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Hazard Severity Score"},
        gauge = {
            'axis': {'range': [0, max_hazard_score]},
            'bar': {'color': hazard_color},
            'steps': [
                {'range': [0, 3.5], 'color': "lightgreen"},
                {'range': [3.5, 6], 'color': "lightyellow"},
                {'range': [6, 8], 'color': "lightcoral"},
                {'range': [8, 10], 'color': "darkred"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': hazard_score
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"**Hazard Level:** {hazard_level} ({hazard_score:.2f}/10)")
    
    # Hazard interpretation
    hazard_descriptions = {
        "Low": "Minor shaking expected. Limited potential for damage to structures.",
        "Moderate": "Moderate shaking expected. Some damage to poorly constructed buildings possible.",
        "High": "Strong shaking expected. Potential for significant damage, especially to older structures.",
        "Very High": "Severe shaking expected. Major damage likely, including to well-built structures."
    }
    
    st.info(hazard_descriptions.get(hazard_level, ""))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Factors affecting hazard
    st.subheader("Factors Affecting Hazard Level")
    
    # Spider/radar chart of factors
    categories = ['Magnitude', 'Shallow Depth', 'Fault Activity', 'Soil Amplification']
    
    # Convert depth to inverse score (shallower = higher hazard)
    depth_factor = 1 - (adjusted_depth / 50)
    
    # Convert fault activity to numeric
    fault_map = {"Low": 0.3, "Medium": 0.6, "High": 1.0}
    fault_score = fault_map.get(city_data['Nearby_Fault_Activity'], 0.5)
    
    # Convert soil type to amplification factor
    soil_map = {"Rock": 0.3, "Stiff": 0.5, "Soft": 0.8, "Very Soft": 1.0}
    soil_score = soil_map.get(selected_soil, 0.5)
    
    # Normalize magnitude to 0-1 scale (assuming range 4-9)
    magnitude_score = (adjusted_magnitude - 4) / 5
    
    values = [magnitude_score, depth_factor, fault_score, soil_score]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Hazard Factors'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Information about the factors
    with st.expander("Understanding Hazard Factors"):
        st.write("""
        - **Magnitude**: Higher magnitude earthquakes release more energy and cause stronger ground motion.
        - **Depth**: Shallow earthquakes (low depth) tend to cause more surface damage than deeper ones.
        - **Fault Activity**: Active fault zones increase the severity of ground motion.
        - **Soil Type**: Soft soils amplify seismic waves, while rocky areas provide more stability.
        """)

# VULNERABILITY MODULE
elif current_tab == "Vulnerability Module":
    st.markdown("<h2 class='module-header'>💥 VULNERABILITY MODULE: Building Damage Assessment</h2>", unsafe_allow_html=True)
    
    # Get hazard level from city data
    city_hazard_level = categorize_hazard_level(city_data["Hazard_Score"])
    
    # User inputs for building information
    col1, col2 = st.columns(2)
    
    with col1:
        building_type = st.selectbox(
            "Building Type:",
            ["Residential", "Commercial", "High-rise", "School", "Hospital", "Industrial"]
        )
        
        building_age = st.slider(
            "Building Age (years):",
            min_value=0,
            max_value=100,
            value=30,
            step=5
        )
        
        building_material = st.selectbox(
            "Building Material:",
            ["Concrete", "Steel", "Brick", "Wood", "Mixed"]
        )
    
    with col2:
        hazard_level = st.selectbox(
            "Hazard Level (from Hazard Module):",
            ["Low", "Moderate", "High", "Very High"],
            index=["Low", "Moderate", "High", "Very High"].index(city_hazard_level) if city_hazard_level in ["Low", "Moderate", "High", "Very High"] else 1
        )
        
        population_density = st.selectbox(
            "Population Density:",
            ["Low", "Medium", "High"]
        )
        
        # Checkbox for additional vulnerability factors
        has_retrofitting = st.checkbox("Building has seismic retrofitting")
        irregular_shape = st.checkbox("Building has irregular shape")
    
    # Calculate vulnerability
    vulnerability_data = {
        'Building_Type': building_type,
        'Building_Age_Years': building_age,
        'Building_Material': building_material,
        'Predicted_Hazard_Level': hazard_level,
        'Population_Density': population_density
    }
    
    # Calculate base vulnerability score
    damage_percent = calculate_vulnerability_score(vulnerability_data)
    
    # Apply modifiers for retrofitting and irregular shape
    if has_retrofitting:
        damage_percent *= 0.7  # 30% reduction
    if irregular_shape:
        damage_percent *= 1.3  # 30% increase
        
    damage_percent = min(100, max(0, damage_percent))  # Ensure between 0-100%
    damage_level = categorize_damage_level(damage_percent)
    
    # Display results
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.subheader("Building Vulnerability Assessment")
    
    # Create gauge for damage percentage
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = damage_percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Estimated Structural Damage"},
        delta = {'reference': 50, 'increasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [0, 100], 'ticksuffix': "%"},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 25], 'color': "lightgreen"},
                {'range': [25, 60], 'color': "lightyellow"},
                {'range': [60, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': damage_percent
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write(f"**Damage Level:** {damage_level}")
    st.write(f"**Estimated Structural Damage:** {damage_percent:.1f}%")
    
    # Casualty potential based on population density and damage level
    casualty_map = {
        "Low": {"Low": "Very Low", "Medium": "Low", "High": "Medium"},
        "Moderate": {"Low": "Low", "Medium": "Medium", "High": "High"},
        "High": {"Low": "Medium", "Medium": "High", "High": "Very High"}
    }
    
    casualty_potential = casualty_map.get(damage_level, {}).get(population_density, "Medium")
    st.write(f"**Casualty Potential:** {casualty_potential} (based on {population_density} population density)")
    
    # Building specific recommendations
    if damage_level == "Low":
        st.success("This building type has good resistance to the expected seismic hazard.")
    elif damage_level == "Moderate":
        st.warning("Consider structural assessment and possible retrofitting to improve seismic resilience.")
    else:
        st.error("This building has high vulnerability. Immediate structural evaluation and reinforcement is recommended.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Vulnerability factors visualization
    st.subheader("Vulnerability Factor Analysis")
    
    # Create bar chart showing contribution of each factor
    material_factor = get_material_factor(building_material) * 100
    age_factor = get_age_factor(building_age) * 100
    density_factor = get_density_factor(population_density) * 100
    hazard_factor = get_hazard_factor(hazard_level) * 100
    
    # Modifiers
    retrofit_factor = 70 if has_retrofitting else 100
    shape_factor = 130 if irregular_shape else 100
    
    factors_df = pd.DataFrame({
        'Factor': ['Material', 'Age', 'Population Density', 'Hazard Level', 'Retrofitting', 'Shape'],
        'Value': [material_factor, age_factor, density_factor, hazard_factor, retrofit_factor, shape_factor],
        'Category': ['Building', 'Building', 'Context', 'Context', 'Modification', 'Modification']
    })
    
    fig = px.bar(
        factors_df, 
        x='Factor', 
        y='Value', 
        color='Category',
        color_discrete_map={
            'Building': '#1E88E5',
            'Context': '#43A047',
            'Modification': '#FFA000'
        },
        labels={'Value': 'Factor Impact (%)', 'Factor': ''},
        title='Relative Impact of Vulnerability Factors (higher = more vulnerable)'
    )
    
    # Add reference line at 100%
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=5.5,
        y0=100,
        y1=100,
        line=dict(color="black", width=2, dash="dash")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Vulnerability matrix
    with st.expander("Vulnerability Matrix Reference"):
        matrix_data = {
            'Material': ['Concrete', 'Steel', 'Brick', 'Wood', 'Mixed'],
            'Age < 10': [25, 20, 40, 30, 35],
            'Age 10-30': [35, 30, 50, 45, 45],
            'Age 30-50': [45, 40, 70, 60, 55],
            'Age > 50': [60, 50, 80, 75, 70]
        }
        
        matrix_df = pd.DataFrame(matrix_data)
        st.write("**Base Damage Percentage by Material and Age (%) under Moderate Hazard**")
        st.dataframe(matrix_df, use_container_width=True)
        
        st.write("""
        **Multipliers:**
        - Low Hazard: 0.5x
        - Moderate Hazard: 1.0x
        - High Hazard: 1.3x
        - Very High Hazard: 1.6x
        
        - Low Density: 0.6x
        - Medium Density: 0.8x
        - High Density: 1.0x
        
        - Seismic Retrofitting: 0.7x
        - Irregular Shape: 1.3x
        """)

# FINANCIAL MODULE
elif current_tab == "Financial Module":
    st.markdown("<h2 class='module-header'>💸 FINANCIAL MODULE: Economic Impact Assessment</h2>", unsafe_allow_html=True)
    
    # Get data from previous modules (in a real app these would be stored in session state)
    city_hazard_level = categorize_hazard_level(city_data["Hazard_Score"])
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # Dropdown to select building details from vulnerability module
        building_type = st.selectbox(
            "Building Type:",
            ["Residential", "Commercial", "High-rise", "School", "Hospital", "Industrial"]
        )
        
        # For demo purposes we'll estimate a damage percentage
        damage_percent = st.slider(
            "Estimated Damage % (from Vulnerability Module):",
            min_value=0,
            max_value=100,
            value=45,
            step=5
        )
        
        # Approximate building size/value
        building_size_options = {
            "Small (≤1,000 sq ft)": 1000,
            "Medium (1,001-5,000 sq ft)": 3000,
            "Large (5,001-10,000 sq ft)": 7500,
            "Very Large (>10,000 sq ft)": 15000
        }
        
        building_size = st.selectbox(
            "Building Size:",
            list(building_size_options.keys())
        )
        
        building_size_value = building_size_options[building_size]
    
    with col2:
        # Number of structures
        num_structures = st.number_input(
            "Number of Structures Affected:",
            min_value=1,
            max_value=10000,
            value=10,
            step=1
        )
        
        # Insurance coverage
        insurance_options = {
            "Fully Insured (90% coverage)": 0.9,
            "Partially Insured (50% coverage)": 0.5,
            "Basic Insurance (25% coverage)": 0.25,
            "No Insurance": 0.0
        }
        
        insurance_status = st.selectbox(
            "Insurance Status:",
            list(insurance_options.keys())
        )
        
        insurance_coverage = insurance_options[insurance_status]
        
        # Optional: custom building value
        custom_value = st.checkbox("Specify custom building value")
        
        if custom_value:
            building_value = st.number_input(
                "Building Value (₹):",
                min_value=100000,
                max_value=1000000000,
                value=2000000,
                step=100000,
                format="%d"
            )
        else:
            # Estimate building value based on type and size
            building_value = estimate_building_value(building_type, building_size_value)
            st.write(f"**Estimated Building Value:** {format_currency(building_value)}")
    
    # Calculate financial impact
    financial_data = {
        'Damage_Percent': damage_percent,
        'Building_Value': building_value,
        'Num_Structures': num_structures,
        'Insurance_Coverage': insurance_coverage
    }
    
    total_loss, insurance_recovery, net_loss = calculate_financial_impact(financial_data)
    
    # Results display
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.subheader("Financial Impact Assessment")
    
    # Create financial impact visualization
    fig = go.Figure()
    
    # Add total loss bar
    fig.add_trace(go.Bar(
        x=['Total Loss'],
        y=[total_loss],
        name='Total Loss',
        marker_color='#FF6B6B'
    ))
    
    # Add insurance recovery bar
    fig.add_trace(go.Bar(
        x=['Insurance Recovery'],
        y=[insurance_recovery],
        name='Insurance Recovery',
        marker_color='#4ECDC4'
    ))
    
    # Add net loss bar
    fig.add_trace(go.Bar(
        x=['Net Loss'],
        y=[net_loss],
        name='Net Loss',
        marker_color='#FF9F1C'
    ))
    
    fig.update_layout(
        title='Financial Impact Breakdown',
        yaxis_title='Amount (₹)',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display financial impact details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Economic Loss",
            format_currency(total_loss),
            delta=None
        )
    
    with col2:
        st.metric(
            "Insurance Recovery",
            format_currency(insurance_recovery),
            delta=None
        )
    
    with col3:
        st.metric(
            "Net Financial Impact",
            format_currency(net_loss),
            delta=None
        )
    
    # Impact severity assessment
    severity_threshold = 5000000  # 50 lakhs threshold for severe impact
    
    if net_loss > severity_threshold:
        st.error(f"The estimated net financial impact is severe. Consider additional risk mitigation strategies.")
    else:
        st.success(f"The estimated net financial impact is manageable with proper insurance coverage.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Additional financial impact analysis
    st.subheader("Impact Scenarios")
    
    # Create scenario comparison
    scenario_options = ["Best Case", "Expected Case", "Worst Case"]
    selected_scenario = st.selectbox("Select Scenario:", scenario_options, index=1)
    
    # Scenario multipliers
    scenario_multipliers = {
        "Best Case": 0.7,
        "Expected Case": 1.0,
        "Worst Case": 1.5
    }
    
    # Calculate scenario impacts
    scenario_multiplier = scenario_multipliers[selected_scenario]
    scenario_damage = min(100, damage_percent * scenario_multiplier)
    scenario_data = {
        'Damage_Percent': scenario_damage,
        'Building_Value': building_value,
        'Num_Structures': num_structures,
        'Insurance_Coverage': insurance_coverage
    }
    
    sc_total_loss, sc_insurance_recovery, sc_net_loss = calculate_financial_impact(scenario_data)
    
    # Display scenario impact
    st.write(f"**{selected_scenario} Scenario:**")
    st.write(f"- Adjusted Damage Percentage: {scenario_damage:.1f}%")
    st.write(f"- Total Economic Loss: {format_currency(sc_total_loss)}")
    st.write(f"- Insurance Recovery: {format_currency(sc_insurance_recovery)}")
    st.write(f"- Net Financial Impact: {format_currency(sc_net_loss)}")
    
    # Time-based recovery cost chart
    st.subheader("Recovery Cost Over Time")
    
    # Create recovery timeline visualization
    recovery_months = 24
    recovery_data = []
    
    # Generate cumulative recovery cost curve
    for month in range(recovery_months + 1):
        # Recovery follows a logarithmic pattern
        if month == 0:
            cumulative_cost = 0
        else:
            recovery_percentage = min(100, 30 * np.log10(month + 1))
            cumulative_cost = sc_net_loss * (recovery_percentage / 100)
        
        recovery_data.append({
            'Month': month,
            'Cumulative Cost': cumulative_cost,
            'Monthly Cost': cumulative_cost - (0 if month == 0 else recovery_data[month-1]['Cumulative Cost'])
        })
    
    recovery_df = pd.DataFrame(recovery_data)
    
    fig = go.Figure()
    
    # Add monthly costs as bars
    fig.add_trace(go.Bar(
        x=recovery_df['Month'],
        y=recovery_df['Monthly Cost'],
        name='Monthly Cost',
        marker_color='#4ECDC4'
    ))
    
    # Add cumulative cost as line
    fig.add_trace(go.Scatter(
        x=recovery_df['Month'],
        y=recovery_df['Cumulative Cost'],
        name='Cumulative Cost',
        marker_color='#FF6B6B',
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='Recovery Cost Timeline',
        xaxis_title='Months After Event',
        yaxis_title='Cost (₹)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    