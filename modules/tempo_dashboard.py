# modules/tempo_dashboard.py
import streamlit as st

def render_tempo_dashboard(games_data, advanced_metrics):
    st.header("⏱️ Tempo & Pace Analysis")
    
    pace_stats = advanced_metrics.get('pace_stats', {})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Pace", f"{pace_stats.get('avg_pace', 0):.1f}")
    col2.metric("Transition %", f"{pace_stats.get('transition_pct', 0):.1%}")
    col3.metric("Half Court %", f"{pace_stats.get('half_court_pct', 0):.1%}")
