"""
DATA PROCESSING MODULE
=======================
Handles all data fetching, transformation, and calculation logic.
"""

import pandas as pd
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
from typing import Tuple

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch production and supplier data from Supabase.
    
    Returns:
        tuple: (production_df, supplier_df)
    """
    prod = supabase.table("production_data").select("*").order("timestamp", desc=True).limit(100).execute().data
    sup = supabase.table("supplier_data").select("*").order("timestamp", desc=True).limit(50).execute().data
    return pd.DataFrame(prod), pd.DataFrame(sup)


def transform_production_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and transform production data.
    
    Args:
        df: Raw production DataFrame
        
    Returns:
        Transformed DataFrame with calculated metrics
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['output_gap'] = df['target_output'] - df['actual_output']
    df['efficiency'] = (df['actual_output'] / df['target_output']) * 100
    
    return df


def transform_supplier_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and transform supplier data.
    
    Args:
        df: Raw supplier DataFrame
        
    Returns:
        Transformed DataFrame with risk indicators
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate supply risk
    df['supply_risk'] = (
        (pd.to_datetime(df['actual_delivery_date']) - 
         pd.to_datetime(df['expected_delivery_date'])).dt.days > 0
    ).replace({True: "Delayed", False: "On Time"})
    
    return df


def calculate_system_health(prod_df: pd.DataFrame, sup_df: pd.DataFrame) -> float:
    """
    Calculate overall system health score (0-100).
    
    Weighted combination of:
    - Production efficiency (40%)
    - Temperature stability (20%)
    - Downtime (20%)
    - Supply chain health (20%)
    
    Args:
        prod_df: Production DataFrame
        sup_df: Supplier DataFrame
        
    Returns:
        Health score (0-100)
    """
    health_components = []
    
    # 1. Production Efficiency Score (40%)
    if not prod_df.empty and 'efficiency' in prod_df.columns:
        avg_efficiency = prod_df['efficiency'].mean()
        eff_score = min(max(avg_efficiency, 0), 100)
        health_components.append(eff_score * 0.4)
    
    # 2. Temperature Stability Score (20%)
    if not prod_df.empty and 'temperature_c' in prod_df.columns:
        temps = prod_df['temperature_c']
        # Ideal: 30-35°C, penalize deviations
        temp_deviation = abs(temps.mean() - 32.5)
        temp_score = max(100 - (temp_deviation * 10), 0)
        health_components.append(temp_score * 0.2)
    
    # 3. Downtime Score (20%)
    if not prod_df.empty and 'downtime_minutes' in prod_df.columns:
        avg_downtime = prod_df['downtime_minutes'].mean()
        downtime_score = max(100 - (avg_downtime * 20), 0)
        health_components.append(downtime_score * 0.2)
    
    # 4. Supply Chain Health (20%)
    if not sup_df.empty and 'supply_risk' in sup_df.columns:
        on_time_count = (sup_df['supply_risk'] == 'On Time').sum()
        total_count = len(sup_df)
        supply_score = (on_time_count / total_count * 100) if total_count > 0 else 50
        health_components.append(supply_score * 0.2)
    
    if not health_components:
        return 50.0
    
    return round(sum(health_components), 1)


def calculate_risk_index(prod_df: pd.DataFrame, sup_df: pd.DataFrame) -> float:
    """
    Calculate overall risk index (0-100, higher = riskier).
    
    Args:
        prod_df: Production DataFrame
        sup_df: Supplier DataFrame
        
    Returns:
        Risk index (0-100)
    """
    risk_factors = []
    
    # 1. Efficiency Risk
    if not prod_df.empty and 'efficiency' in prod_df.columns:
        avg_efficiency = prod_df['efficiency'].mean()
        eff_risk = max(100 - avg_efficiency, 0)
        risk_factors.append(eff_risk * 0.3)
    
    # 2. Temperature Risk
    if not prod_df.empty and 'temperature_c' in prod_df.columns:
        max_temp = prod_df['temperature_c'].max()
        temp_risk = max((max_temp - 35) * 20, 0)
        risk_factors.append(min(temp_risk, 100) * 0.3)
    
    # 3. Supply Delay Risk
    if not sup_df.empty and 'supply_risk' in sup_df.columns:
        delayed_pct = (sup_df['supply_risk'] == 'Delayed').sum() / len(sup_df) * 100
        risk_factors.append(delayed_pct * 0.4)
    
    if not risk_factors:
        return 30.0
    
    return round(min(sum(risk_factors), 100), 1)
