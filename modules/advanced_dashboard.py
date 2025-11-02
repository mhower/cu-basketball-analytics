# modules/advanced_dashboard.py
import streamlit as st
import plotly.express as px
import pandas as pd

def render_advanced_dashboard(games_data, players_data, advanced_metrics):
    st.header("⚡ Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Momentum", "WPA Leaders", "Close Games"])
    
    with tab1:
        st.subheader("🔥 Scoring Runs & Momentum")
        runs = advanced_metrics.get('momentum_runs', [])
        
        if runs:
            for run in runs[:10]:
                st.write(f"**{run.get('team')}** - {run.get('length', 0)} point run")
                st.write(f"Game: {run.get('game_id')} vs {run.get('opponent')}")
                st.markdown("---")
        else:
            st.info("No momentum data available")
    
    with tab2:
        st.subheader("📊 Win Probability Added Leaders")
        st.info("WPA calculations require play-by-play analysis")
    
    with tab3:
        st.subheader("🎯 Close Game Performance")
        close_performers = []
        for player in players_data:
            metrics = player.get('metrics', {})
            if metrics.get('Close Game PPG', 0) > 5:
                close_performers.append({
                    'Player': player['name'],
                    'Close PPG': metrics.get('Close Game PPG', 0),
                    'Close FG%': metrics.get('Close Game FG%', 0)
                })
        
        if close_performers:
            df = pd.DataFrame(close_performers)
            st.dataframe(df, use_container_width=True)
