# modules/defense_dashboard.py
import streamlit as st
import pandas as pd

def render_defense_dashboard(players_data, games_data):
    st.header("🛡️ Defensive Analysis")
    
    defensive_leaders = []
    for player in players_data:
        metrics = player.get('metrics', {})
        defensive_leaders.append({
            'Player': player['name'],
            'Steals Per 40': metrics.get('Steals Per 40', 0),
            'Blocks Per 40': metrics.get('Blocks Per 40', 0),
            'Def Rating': metrics.get('Defensive Rating', 0),
            'DReb %': metrics.get('Defensive Rebound %', 0)
        })
    
    df = pd.DataFrame(defensive_leaders)
    df = df.sort_values('Steals Per 40', ascending=False)
    
    st.subheader("Top Defenders")
    st.dataframe(df, use_container_width=True)
