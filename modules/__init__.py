"""
Earthquake Risk Assessment Modules

This package contains modules for the earthquake catastrophe modeling system:
- Event Module: Predicts likelihood of earthquake occurring
- Hazard Module: Estimates severity if an earthquake occurs
- Vulnerability Module: Assesses potential damage to structures
- Financial Module: Calculates economic impact
"""

from .event_module import calculate_event_score, assign_event_risk_zone
from .hazard_module import calculate_hazard_score, categorize_hazard_level
from .vulnerability_module import (
    get_material_factor, get_age_factor, get_density_factor, get_hazard_factor,
    calculate_vulnerability_score, categorize_damage_level
)
from .financial_module import estimate_building_value, calculate_financial_impact
from .utils import load_data, format_currency