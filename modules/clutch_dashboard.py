# modules/clutch_dashboard.py
import streamlit as st
import pandas as pd

def render_clutch_dashboard(players_data, games_data):
    st.header("🎯 Clutch Performance")
    
    clutch_players = []
    for player in players_data:
        metrics = player.get('metrics', {})
        clutch_rating = metrics.get('Clutch Rating', 0)
        if clutch_rating > 40:
            clutch_players.append({
                'Player': player['name'],
                'Clutch Rating': clutch_rating,
                'Close PPG': metrics.get('Close Game PPG', 0),
                'Close FG%': metrics.get('Close Game FG%', 0)
            })
    
    if clutch_players:
        df = pd.DataFrame(clutch_players)
        df = df.sort_values('Clutch Rating', ascending=False)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No clutch performance data available")
