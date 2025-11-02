# modules/lineup_dashboard.py
import streamlit as st
import pandas as pd

def render_lineup_dashboard(analyzer):
    st.header("🔀 Lineup Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Top Lineups", "2-Player Combos", "Optimizer"])
    
    with tab1:
        st.subheader("Top 5-Player Lineups")
        lineups = analyzer.get_top_lineups(10)
        
        for idx, (players, stats) in enumerate(lineups, 1):
            st.markdown(f"**#{idx}:** {', '.join(players)}")
            st.write(f"Games: {stats['games']} | Plus/Minus: {stats.get('plus_minus', 0):.1f}")
            st.markdown("---")
    
    with tab2:
        st.subheader("Top 2-Player Combinations")
        combos = analyzer.get_two_player_combos()
        sorted_combos = sorted(combos.items(), key=lambda x: x[1]['games'], reverse=True)[:20]
        
        for (p1, p2), stats in sorted_combos:
            col1, col2 = st.columns([3, 1])
            col1.write(f"{p1} + {p2}")
            col2.metric("Games", stats['games'])
    
    with tab3:
        st.subheader("Lineup Optimizer")
        situation = st.selectbox("Situation", ["Closing", "Offense", "Defense"])
        
        if st.button("Generate Optimal Lineup"):
            optimal = analyzer.optimize_lineup(situation.lower())
            st.success(f"Optimal {situation} Lineup:")
            for player in optimal:
                st.write(f"• {player}")
