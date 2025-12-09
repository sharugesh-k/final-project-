"""
UI COMPONENTS MODULE
=====================
Reusable UI components for executive dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_kpi_card(label: str, value: str, delta: Optional[str] = None, 
                   trend: Optional[str] = None, delta_color: str = "normal"):
    """
    Render KPI card with trend indicator.
    
    Args:
        label: KPI label
        value: KPI value
        delta: Change value
        trend: Trend indicator (↑ or ↓)
        delta_color: Color for delta ("normal", "inverse", "off")
    """
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
    with col2:
        if trend:
            st.markdown(f"<h2 style='text-align: center; margin-top: 20px;'>{trend}</h2>", 
                       unsafe_allow_html=True)


def render_health_gauge(score: float, title: str = "System Health Score"):
    """
    Render health score gauge (0-100).
    
    Args:
        score: Health score
        title: Gauge title
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 80, 'increasing': {'color': "#00cc96"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#00cc96" if score >= 80 else "#ff8800" if score >= 60 else "#ff4444"},
            'steps': [
                {'range': [0, 60], 'color': 'rgba(255, 68, 68, 0.2)'},
                {'range': [60, 80], 'color': 'rgba(255, 136, 0, 0.2)'},
                {'range': [80, 100], 'color': 'rgba(0, 204, 150, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Segoe UI"},
        height=300
    )
    
    return fig


def render_risk_gauge(risk_index: float, title: str = "Risk Index"):
    """
    Render risk index gauge (0-100, higher = riskier).
    
    Args:
        risk_index: Risk score
        title: Gauge title
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_index,
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 50, 'increasing': {'color': "#ff4444"}, 'decreasing': {'color': "#00cc96"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#ff4444" if risk_index >= 70 else "#ff8800" if risk_index >= 40 else "#00cc96"},
            'steps': [
                {'range': [0, 40], 'color': 'rgba(0, 204, 150, 0.2)'},
                {'range': [40, 70], 'color': 'rgba(255, 136, 0, 0.2)'},
                {'range': [70, 100], 'color': 'rgba(255, 68, 68, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Segoe UI"},
        height=300
    )
    
    return fig


def render_alert_banner(message: str):
    """
    Render persistent critical alert banner.
    
    Args:
        message: Banner message
    """
    st.markdown(f"""
    <div style="background-color: #ff4444; padding: 20px; border-radius: 10px; 
                border-left: 5px solid #cc0000; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; font-weight: bold;">
            🚨 CRITICAL SYSTEM ALERT
        </h3>
        <p style="color: white; margin: 10px 0 0 0; font-size: 16px; line-height: 1.6;">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_chart_with_guidance(fig, what: str, why: str, action: str):
    """
    Render chart with explanatory guidance.
    
    Args:
        fig: Plotly figure
        what: What this means
        why: Why this matters
        action: What to do next
    """
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📘 Chart Guidance", expanded=False):
        st.markdown(f"""
        **🔍 What this means:**  
        {what}
        
        **💡 Why this matters:**  
        {why}
        
        **✅ What to do next:**  
        {action}
        """)


def render_recommendation_card(category: str, recommendations: list, icon: str = "💡"):
    """
    Render AI recommendation card.
    
    Args:
        category: Recommendation category
        recommendations: List of recommendation strings
        icon: Category icon
    """
    colors = {
        "Immediate Action": "#ff4444",
        "Short-Term Fix": "#ff8800",
        "Long-Term Strategy": "#4488ff"
    }
    
    color = colors.get(category, "#888888")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                padding: 15px; border-radius: 10px; border-left: 4px solid {color}; margin-bottom: 15px;">
        <h4 style="color: {color}; margin: 0 0 10px 0;">
            {icon} {category}
        </h4>
        <ul style="margin: 0; padding-left: 20px; color: #e0e0e0;">
    """, unsafe_allow_html=True)
    
    for rec in recommendations:
        st.markdown(f"<li style='margin-bottom: 5px;'>{rec}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)


def render_tooltip(text: str, help_text: str):
    """
    Render text with tooltip.
    
    Args:
        text: Display text
        help_text: Tooltip text
    """
    st.markdown(f"""
    <span style="border-bottom: 1px dotted #888; cursor: help;" title="{help_text}">
        {text} ℹ️
    </span>
    """, unsafe_allow_html=True)


def apply_color_psychology(value: float, thresholds: dict) -> str:
    """
    Apply color based on value and thresholds.
    
    Args:
        value: Value to evaluate
        thresholds: Dictionary with 'critical', 'warning', 'healthy' thresholds
        
    Returns:
        Color hex code
    """
    if value >= thresholds.get('critical', 80):
        return '#ff4444'  # Red - Critical
    elif value >= thresholds.get('warning', 50):
        return '#ff8800'  # Orange - Warning
    else:
        return '#00cc96'  # Green - Healthy


def render_trend_indicator(current: float, previous: float) -> str:
    """
    Calculate and return trend indicator.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Trend symbol (↑ or ↓)
    """
    return "↑" if current > previous else "↓" if current < previous else "→"


def render_loading_skeleton():
    """Render loading skeleton UI."""
    with st.spinner('Loading dashboard data...'):
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); height: 100px; 
                    border-radius: 10px; margin-bottom: 10px; animation: pulse 1.5s infinite;">
        </div>
        <style>
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.8; }
        }
        </style>
        """, unsafe_allow_html=True)
