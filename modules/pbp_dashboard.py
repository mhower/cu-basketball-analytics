# modules/pbp_dashboard.py
import streamlit as st
import pandas as pd

def render_pbp_dashboard(pbp_analyzer):
    st.header("🎲 Play-by-Play Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Scoring Plays", "Momentum", "Stats"])
    
    with tab1:
        st.subheader("Recent Scoring Plays")
        scoring = pbp_analyzer.get_scoring_plays()
        
        if scoring:
            for play in scoring[-20:]:
                st.write(f"{play.get('time', '?')} - {play.get('player', 'Unknown')}: {play.get('action', '')}")
        else:
            st.info("No scoring plays found")
    
    with tab2:
        st.subheader("🔥 Momentum Swings")
        swings = pbp_analyzer.get_momentum_swings()
        
        if swings:
            for swing in swings[:10]:
                st.write(f"**{swing.get('game')}** - Q{swing.get('period')} {swing.get('time')}")
                st.write(f"Swing: {swing.get('swing')} points")
                st.markdown("---")
    
    with tab3:
        st.subheader("📊 Play Statistics")
        st.metric("Total Plays", len(pbp_analyzer.all_plays))
