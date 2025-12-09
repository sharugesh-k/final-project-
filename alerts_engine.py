"""
ALERTS ENGINE MODULE
=====================
Intelligent alert detection and prioritization.
"""

import pandas as pd
import numpy as np
from typing import List, Dict


def detect_anomalies(df: pd.DataFrame, column: str, sensitivity: float = 2.0) -> pd.Series:
    """
    Detect anomalies using Z-score method.
    
    Args:
        df: DataFrame
        column: Column to analyze
        sensitivity: Z-score threshold
        
    Returns:
        Boolean series marking anomalies
    """
    if df.empty or column not in df.columns:
        return pd.Series(dtype=bool)
    
    series = df[column]
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return pd.Series([False] * len(series))
    
    z_scores = np.abs((series - mean) / std)
    return z_scores > sensitivity


def detect_spike(df: pd.DataFrame, column: str, sensitivity: float = 2.0) -> pd.Series:
    """Detect abnormal upward spikes."""
    if df.empty or column not in df.columns:
        return pd.Series(dtype=bool)
    
    series = df[column]
    mean, std = series.mean(), series.std()
    
    if std == 0:
        return pd.Series([False] * len(series))
    
    threshold = mean + (sensitivity * std)
    return series > threshold


def detect_drop(df: pd.DataFrame, column: str, sensitivity: float = 2.0) -> pd.Series:
    """Detect sudden drops."""
    if df.empty or column not in df.columns:
        return pd.Series(dtype=bool)
    
    series = df[column]
    mean, std = series.mean(), series.std()
    
    if std == 0:
        return pd.Series([False] * len(series))
    
    threshold = mean - (sensitivity * std)
    return series < threshold


def generate_alerts(prod_df: pd.DataFrame, sup_df: pd.DataFrame, 
                   sensitivity: float = 1.5) -> List[Dict]:
    """
    Generate intelligent alerts based on data patterns.
    
    Args:
        prod_df: Production DataFrame
        sup_df: Supplier DataFrame
        sensitivity: Alert sensitivity (1.0-3.0, lower = more alerts)
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    
    if prod_df.empty:
        return alerts
    
    # 1. Low Efficiency Alerts
    low_eff_machines = prod_df[prod_df['efficiency'] < 70]['machine_id'].unique()
    for machine in low_eff_machines:
        machine_data = prod_df[prod_df['machine_id'] == machine]
        avg_eff = machine_data['efficiency'].mean()
        alerts.append({
            "severity": "CRITICAL",
            "category": "Production",
            "message": f"Machine {machine} efficiency critically low at {avg_eff:.1f}%",
            "recommendation": f"Immediate inspection required for {machine}. Check mechanical systems and calibration.",
            "focus_area": "Machine Maintenance",
            "priority": 1
        })
    
    # 2. Temperature Alerts
    high_temp = detect_spike(prod_df, 'temperature_c', sensitivity)
    if high_temp.any():
        max_temp = prod_df.loc[high_temp, 'temperature_c'].max()
        affected_machines = prod_df.loc[high_temp, 'machine_id'].unique()
        alerts.append({
            "severity": "CRITICAL" if max_temp > 40 else "WARNING",
            "category": "Safety",
            "message": f"Temperature spike detected: {max_temp:.1f}°C on {', '.join(affected_machines)}",
            "recommendation": "Activate cooling systems. Reduce production load if temperature persists above 38°C.",
            "focus_area": "Cooling Systems",
            "priority": 1 if max_temp > 40 else 2
        })
    
    # 3. Downtime Anomalies
    downtime_anomalies = detect_spike(prod_df, 'downtime_minutes', sensitivity)
    if downtime_anomalies.any():
        avg_downtime = prod_df.loc[downtime_anomalies, 'downtime_minutes'].mean()
        alerts.append({
            "severity": "WARNING",
            "category": "Operational",
            "message": f"Abnormal downtime detected: {avg_downtime:.1f} minutes average",
            "recommendation": "Investigate recent maintenance activities. Check for recurring fault patterns.",
            "focus_area": "Downtime Reduction",
            "priority": 2
        })
    
    # 4. Supply Chain Alerts
    if not sup_df.empty and 'supply_risk' in sup_df.columns:
        delayed = sup_df[sup_df['supply_risk'] == 'Delayed']
        if len(delayed) > 0:
            delayed_count = len(delayed)
            delayed_suppliers = delayed['supplier_id'].unique()
            alerts.append({
                "severity": "WARNING" if delayed_count <= 2 else "CRITICAL",
                "category": "Supply Chain",
                "message": f"{delayed_count} delayed deliveries from {', '.join(delayed_suppliers)}",
                "recommendation": "Contact suppliers for expedited shipping. Activate backup supplier contracts.",
                "focus_area": "Supplier Lead Time",
                "priority": 2 if delayed_count <= 2 else 1
            })
    
    # 5. Efficiency Drop Trend
    if len(prod_df) >= 10:
        recent_eff = prod_df.tail(10)['efficiency'].mean()
        older_eff = prod_df.head(10)['efficiency'].mean()
        eff_drop = older_eff - recent_eff
        
        if eff_drop > 10:
            alerts.append({
                "severity": "WARNING",
                "category": "Trend Analysis",
                "message": f"Efficiency declining trend detected: -{eff_drop:.1f}% over recent period",
                "recommendation": "Conduct comprehensive system audit. Review maintenance schedules.",
                "focus_area": "System Performance",
                "priority": 2
            })
    
    return sorted(alerts, key=lambda x: x['priority'])


def prioritize_alerts(alerts: List[Dict]) -> List[Dict]:
    """
    Sort and prioritize alerts.
    
    Args:
        alerts: List of alert dictionaries
        
    Returns:
        Prioritized alerts
    """
    return sorted(alerts, key=lambda x: (x.get('priority', 99), x.get('severity', 'INFO')))


def create_banner_message(alerts: List[Dict]) -> str:
    """
    Create persistent warning banner message.
    
    Args:
        alerts: List of alerts
        
    Returns:
        Banner message string
    """
    critical_alerts = [a for a in alerts if a.get('severity') == 'CRITICAL']
    
    if not critical_alerts:
        return ""
    
    top_alert = critical_alerts[0]
    count = len(critical_alerts)
    
    focus = top_alert.get('focus_area', 'System Health')
    reason = top_alert.get('message', 'Multiple critical issues detected')
    
    banner = f"⚠️ IMMEDIATE ATTENTION REQUIRED: {count} CRITICAL ISSUE{'S' if count > 1 else ''}\n"
    banner += f"PRIMARY FOCUS: {focus}\n"
    banner += f"REASON: {reason}"
    
    return banner


def get_alert_color(severity: str) -> str:
    """Get color for alert severity."""
    colors = {
        'CRITICAL': '#ff4444',
        'WARNING': '#ff8800',
        'SAFE': '#00cc66',
        'INFO': '#4488ff'
    }
    return colors.get(severity, '#888888')
