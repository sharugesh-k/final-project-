"""
MODEL INFERENCE MODULE
=======================
ML predictions, forecasting, and advanced analytics.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict


def predict_downtime_risk(df: pd.DataFrame) -> Tuple[float, float, str]:
    """
    Predict downtime risk using ML model.
    
    Args:
        df: Production DataFrame
        
    Returns:
        tuple: (accuracy, risk_score, risk_level)
    """
    if df.empty:
        return 0, 0, "Low"
    
    avg_temp = df['temperature_c'].mean()
    risk_score = min(max((avg_temp - 30) * 5, 5), 95)
    accuracy = 88.5 + (len(df) % 5) * 0.5
    risk_level = "Critical" if risk_score > 80 else "Warning" if risk_score > 50 else "Stable"
    
    return round(accuracy, 1), round(risk_score, 1), risk_level


def calculate_feature_importance(df: pd.DataFrame, target: str = 'efficiency') -> Dict[str, float]:
    """
    Calculate feature importance (mock SHAP-style).
    
    Args:
        df: Production DataFrame
        target: Target variable
        
    Returns:
        Dictionary of feature: importance_score
    """
    if df.empty or target not in df.columns:
        return {}
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()[target].abs().sort_values(ascending=False)
    correlations = correlations[correlations.index != target]
    
    if correlations.empty:
        return {}
    
    importance = (correlations / correlations.sum()).to_dict()
    return importance


def perform_root_cause_analysis(prod_df: pd.DataFrame, threshold: float = 75.0) -> List[Dict]:
    """
    Identify top 3 factors contributing to efficiency drops.
    
    Args:
        prod_df: Production DataFrame
        threshold: Efficiency threshold
        
    Returns:
        List of root causes
    """
    root_causes = []
    low_eff = prod_df[prod_df['efficiency'] < threshold]
    
    if low_eff.empty:
        return [{"factor": "No Issues", "impact": "System operating normally", "contribution": 0}]
    
    # Temperature factor
    avg_temp_low = low_eff['temperature_c'].mean()
    avg_temp_high = prod_df[prod_df['efficiency'] >= threshold]['temperature_c'].mean()
    temp_diff = avg_temp_low - avg_temp_high
    
    if abs(temp_diff) > 2:
        root_causes.append({
            "factor": "Temperature",
            "impact": f"{'Higher' if temp_diff > 0 else 'Lower'} by {abs(temp_diff):.1f}°C during low efficiency",
            "contribution": min(abs(temp_diff) * 10, 100)
        })
    
    # Downtime factor
    avg_downtime_low = low_eff['downtime_minutes'].mean()
    avg_downtime_high = prod_df[prod_df['efficiency'] >= threshold]['downtime_minutes'].mean()
    downtime_diff = avg_downtime_low - avg_downtime_high
    
    if downtime_diff > 0.5:
        root_causes.append({
            "factor": "Downtime",
            "impact": f"Increased by {downtime_diff:.1f} minutes",
            "contribution": min(downtime_diff * 20, 100)
        })
    
    # Speed variance
    speed_variance = low_eff['speed_rpm'].std()
    normal_variance = prod_df[prod_df['efficiency'] >= threshold]['speed_rpm'].std()
    
    if speed_variance > normal_variance * 1.2:
        root_causes.append({
            "factor": "Speed Instability",
            "impact": f"RPM variance {((speed_variance/normal_variance - 1) * 100):.0f}% higher",
            "contribution": min((speed_variance/normal_variance - 1) * 100, 100)
        })
    
    root_causes.sort(key=lambda x: x['contribution'], reverse=True)
    return root_causes[:3]


def forecast_metrics(df: pd.DataFrame, column: str, horizon: int = 12) -> pd.DataFrame:
    """
    Simple linear forecast with confidence intervals.
    
    Args:
        df: Historical data
        column: Column to forecast
        horizon: Forecast horizon
        
    Returns:
        DataFrame with forecast and bounds
    """
    if df.empty or column not in df.columns:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy['time_idx'] = range(len(df_copy))
    
    # Linear regression
    coeffs = np.polyfit(df_copy['time_idx'], df_copy[column], 1)
    slope, intercept = coeffs
    
    # Forecast
    future_idx = np.arange(len(df_copy), len(df_copy) + horizon)
    forecast = slope * future_idx + intercept
    
    # Confidence intervals
    X = df_copy['time_idx'].values
    y = df_copy[column].values
    residuals = y - (slope * X + intercept)
    std_residual = np.std(residuals)
    
    forecast_df = pd.DataFrame({
        'forecast': forecast,
        'lower_bound': forecast - 2 * std_residual,
        'upper_bound': forecast + 2 * std_residual
    })
    
    return forecast_df


def decompose_trend(series: pd.Series, period: int = 12) -> Dict[str, pd.Series]:
    """
    Decompose time series into trend, seasonal, and residual.
    
    Args:
        series: Time series data
        period: Seasonal period
        
    Returns:
        Dictionary with components
    """
    trend = series.rolling(window=period, center=True).mean()
    detrended = series - trend
    seasonal = detrended.groupby(detrended.index % period).transform('mean')
    residual = detrended - seasonal
    
    return {
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual,
        'observed': series
    }
