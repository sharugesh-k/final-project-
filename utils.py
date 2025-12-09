"""
UTILITIES MODULE
=================
Helper functions for export, calculations, and formatting.
"""

import pandas as pd
import base64
from io import BytesIO


def export_to_csv(data: pd.DataFrame, filename: str = "export.csv") -> bytes:
    """
    Export DataFrame to CSV.
    
    Args:
        data: DataFrame to export
        filename: Output filename
        
    Returns:
        CSV bytes
    """
    return data.to_csv(index=False).encode('utf-8')


def create_download_link(data: bytes, filename: str, link_text: str = "Download") -> str:
    """
    Create download link for data.
    
    Args:
        data: File data as bytes
        filename: Download filename
        link_text: Link display text
        
    Returns:
        HTML download link
    """
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href


def calculate_trend_indicator(current: float, previous: float) -> str:
    """
    Calculate trend indicator symbol.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Trend symbol (↑, ↓, →)
    """
    if current > previous:
        return "↑"
    elif current < previous:
        return "↓"
    else:
        return "→"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 1) -> str:
    """Format number with thousand separators."""
    return f"{value:,.{decimals}f}"


def get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level."""
    emojis = {
        'CRITICAL': '🔴',
        'WARNING': '🟡',
        'SAFE': '🟢',
        'INFO': '🔵'
    }
    return emojis.get(severity, '⚪')


def generate_insight_summary(health_score: float, risk_index: float, 
                            alerts_count: int) -> str:
    """
    Generate one-sentence AI insight summary.
    
    Args:
        health_score: System health (0-100)
        risk_index: Risk index (0-100)
        alerts_count: Number of critical alerts
        
    Returns:
        Insight sentence
    """
    if health_score >= 80:
        return f"✅ System operating at optimal levels with {health_score:.0f}% health score. Continue monitoring routine parameters."
    elif health_score >= 60:
        insight = f"⚠️ System health at {health_score:.0f}% with {alerts_count} active alert(s). "
        if risk_index >= 60:
            insight += "Immediate attention required on high-risk areas to prevent deterioration."
        else:
            insight += "Proactive maintenance recommended to restore optimal performance."
        return insight
    else:
        return f"🚨 CRITICAL: System health critically low at {health_score:.0f}%. Immediate intervention required across {alerts_count} alert areas."


def simulate_what_if(current_health: float, current_risk: float, 
                     efficiency_change: float = 0, temp_change: float = 0, 
                     supply_improvement: float = 0) -> dict:
    """
    Simulate What-If scenario impact.
    
    Args:
        current_health: Current health score
        current_risk: Current risk index
        efficiency_change: % change in efficiency
        temp_change: °C change in temperature
        supply_improvement: % improvement in supply chain
        
    Returns:
        Dictionary with projected metrics
    """
    # Impact weights
    eff_impact = efficiency_change * 0.4
    temp_impact = -abs(temp_change) * 2 * 0.2
    supply_impact = supply_improvement * 0.2
    
    projected_health = min(max(current_health + eff_impact + temp_impact + supply_impact, 0), 100)
    projected_risk = min(max(100 - projected_health, 0), 100)
    
    return {
        'projected_health': round(projected_health, 1),
        'projected_risk': round(projected_risk, 1),
        'health_change': round(projected_health - current_health, 1),
        'risk_change': round(current_risk - projected_risk, 1),
        'cost_impact': round(abs(projected_health - current_health) * 500, 0)  # Mock cost
    }
