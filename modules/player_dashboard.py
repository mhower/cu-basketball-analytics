# modules/player_dashboard.py
# Player dashboard rendering

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_player_dashboard(players_data, games_data):
    """Render complete player analysis dashboard"""
    
    st.header("👥 Player Performance Analysis")
    
    if not players_data:
        st.warning("No player data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_metric = st.selectbox(
            "Sort By",
            ["PPG", "RPG", "APG", "eFG%", "PER", "Plus/Minus"]
        )
    
    with col2:
        position_filter = st.selectbox(
            "Position",
            ["All", "G", "F", "C"]
        )
    
    with col3:
        min_mpg = st.slider("Min MPG", 0, 40, 5)
    
    # Filter players
    filtered_players = players_data
    if position_filter != "All":
        filtered_players = [p for p in filtered_players 
                          if p.get('position', 'F').startswith(position_filter)]
    
    filtered_players = [p for p in filtered_players 
                       if p.get('metrics', {}).get('MPG', 0) >= min_mpg]
    
    # Sort players
    sorted_players = sorted(
        filtered_players,
        key=lambda x: x.get('metrics', {}).get(sort_metric, 0),
        reverse=True
    )
    
    # Display player cards
    for player in sorted_players:
        with st.expander(f"**{player['name']}** - {player.get('position', 'F')}", expanded=False):
            render_player_card(player)

def render_player_card(player):
    """Render detailed player card"""
    metrics = player.get('metrics', {})
    
    # Basic stats
    st.subheader("📊 Basic Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("PPG", f"{metrics.get('PPG', 0):.1f}")
    col2.metric("RPG", f"{metrics.get('RPG', 0):.1f}")
    col3.metric("APG", f"{metrics.get('APG', 0):.1f}")
    col4.metric("FG%", f"{metrics.get('FG%', 0):.1%}")
    col5.metric("MPG", f"{metrics.get('MPG', 0):.1f}")
    
    st.markdown("---")
    
    # Advanced metrics
    st.subheader("🎯 Advanced Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("eFG%", f"{metrics.get('eFG%', 0):.1%}")
    col2.metric("TS%", f"{metrics.get('TS%', 0):.1%}")
    col3.metric("PER", f"{metrics.get('PER', 0):.1f}")
    col4.metric("Usage", f"{metrics.get('Usage Rate', 0):.1%}")
    
    st.markdown("---")
    
    # Quarter performance
    st.subheader("📈 Quarter Performance")
    
    quarter_data = {
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
        'PPG': [
            metrics.get('Q1 PPG', 0),
            metrics.get('Q2 PPG', 0),
            metrics.get('Q3 PPG', 0),
            metrics.get('Q4 PPG', 0)
        ],
        'FG%': [
            metrics.get('Q1 FG%', 0) * 100,
            metrics.get('Q2 FG%', 0) * 100,
            metrics.get('Q3 FG%', 0) * 100,
            metrics.get('Q4 FG%', 0) * 100
        ]
    }
    
    df_quarters = pd.DataFrame(quarter_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_quarters['Quarter'],
        y=df_quarters['PPG'],
        name='PPG',
        marker_color='#CFB87C'
    ))
    
    fig.update_layout(
        height=300,
        yaxis_title="Points Per Game",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Consistency
    st.subheader("📊 Consistency & Reliability")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Type", metrics.get('Player Type', 'N/A'))
    col2.metric("Consistency", f"{metrics.get('Consistency Rating', 0):.0f}/100")
    col3.metric("Std Dev", f"{metrics.get('Scoring Std Dev', 0):.1f}")
    
    # Opponent performance
    st.subheader("🎯 Opponent Performance")
    opp_stats = metrics.get('Opponent Stats', {})
    
    if opp_stats:
        opp_data = []
        for opp, stats in opp_stats.items():
            opp_data.append({
                'Opponent': opp,
                'PPG': stats.get('PPG', 0),
                'FG%': stats.get('FG%', 0),
                'Games': stats.get('Games', 0)
            })
        
        df_opp = pd.DataFrame(opp_data)
        st.dataframe(df_opp, use_container_width=True)
