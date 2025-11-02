# modules/rotation_dashboard.py
import streamlit as st

def render_rotation_dashboard(players_data, games_data):
    st.header("🔄 Rotation Patterns")
    
    st.subheader("Substitution Analysis")
    
    for player in players_data[:10]:
        metrics = player.get('metrics', {})
        st.write(f"**{player['name']}**")
        col1, col2 = st.columns(2)
        col1.metric("Avg Stint", f"{metrics.get('Avg Stint Length', 0):.1f} min")
        col2.metric("Subs/Game", f"{metrics.get('Substitutions Per Game', 0):.1f}")
        st.markdown("---")
