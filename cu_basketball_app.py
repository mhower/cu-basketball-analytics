# CU Women's Basketball Analytics - Complete Streamlit Application
# Version 13.0 - Full Implementation with ALL Metrics
# Run: streamlit run cu_basketball_app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from pathlib import Path

# Import custom modules
from modules.data_loader import GameDataLoader
from modules.metrics_calculator import MetricsCalculator
from modules.visualization import VisualizationEngine
from modules.lineup_analyzer import LineupAnalyzer
from modules.play_analyzer import PlayByPlayAnalyzer
from modules.export_manager import ExportManager

# Page configuration
st.set_page_config(
    page_title="CU Women's Basketball Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .player-card {
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
        border-radius: 5px;
    }
    .stat-highlight {
        background-color: #ffffcc;
        padding: 2px 5px;
        border-radius: 3px;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'games_data' not in st.session_state:
    st.session_state.games_data = None
if 'players_data' not in st.session_state:
    st.session_state.players_data = None
if 'advanced_metrics' not in st.session_state:
    st.session_state.advanced_metrics = None

# Sidebar - Data Loading and Configuration
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/000000/FFD700?text=CU+BUFFS", use_container_width=True)
    st.title("🏀 CU Basketball Analytics")
    st.markdown("---")
    
    # Data source selection
    st.subheader("📁 Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["Local XML Files", "Upload Files", "Google Drive (Coming Soon)"],
        index=0
    )
    
    # Load data based on source
    if data_source == "Local XML Files":
        xml_directory = st.text_input("XML Directory Path", "/mnt/project")
        load_button = st.button("🔄 Load Games", type="primary", use_container_width=True)
        
        if load_button or st.session_state.data_loaded:
            with st.spinner("Loading game data..."):
                try:
                    loader = GameDataLoader(xml_directory)
                    games_data = loader.load_all_games()
                    
                    if games_data:
                        st.session_state.games_data = games_data
                        st.session_state.data_loaded = True
                        
                        # Calculate metrics
                        calculator = MetricsCalculator(games_data)
                        st.session_state.players_data = calculator.calculate_all_player_metrics()
                        st.session_state.advanced_metrics = calculator.calculate_advanced_metrics()
                        
                        st.success(f"✅ Loaded {len(games_data)} games successfully!")
                        st.metric("Total Games", len(games_data))
                        st.metric("Total Players", len(st.session_state.players_data))
                    else:
                        st.error("❌ No games found in directory")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
    
    elif data_source == "Upload Files":
        uploaded_files = st.file_uploader(
            "Upload XML game files",
            type=['xml'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            with st.spinner("Processing uploaded files..."):
                try:
                    loader = GameDataLoader()
                    games_data = loader.load_from_uploads(uploaded_files)
                    
                    if games_data:
                        st.session_state.games_data = games_data
                        st.session_state.data_loaded = True
                        
                        calculator = MetricsCalculator(games_data)
                        st.session_state.players_data = calculator.calculate_all_player_metrics()
                        st.session_state.advanced_metrics = calculator.calculate_advanced_metrics()
                        
                        st.success(f"✅ Processed {len(games_data)} games!")
                except Exception as e:
                    st.error(f"Error processing files: {str(e)}")
    
    st.markdown("---")
    
    # Filters (when data is loaded)
    if st.session_state.data_loaded:
        st.subheader("🔍 Filters")
        
        # Date range filter
        if st.session_state.games_data:
            all_dates = [g.get('date_obj') for g in st.session_state.games_data if g.get('date_obj')]
            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)
                
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        # Opponent filter
        opponents = ["All"] + sorted(list(set([
            g.get('opponent', 'Unknown') 
            for g in st.session_state.games_data
        ])))
        selected_opponent = st.selectbox("Opponent", opponents)
        
        # Home/Away filter
        location_filter = st.selectbox("Location", ["All", "Home", "Away"])
        
        # Result filter
        result_filter = st.selectbox("Result", ["All", "Wins", "Losses"])
        
        # Minimum minutes filter
        min_minutes = st.slider("Min Minutes Per Game", 0, 40, 5)
        
        st.markdown("---")
        
        # Export options
        st.subheader("📤 Export")
        
        if st.button("📊 Export to JSON", use_container_width=True):
            exporter = ExportManager(st.session_state.games_data, st.session_state.players_data)
            json_path = exporter.export_json()
            st.success(f"Exported to: {json_path}")
            
            with open(json_path, 'rb') as f:
                st.download_button(
                    "⬇️ Download JSON",
                    f,
                    file_name="cu_basketball_data.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        if st.button("📄 Export to HTML Report", use_container_width=True):
            exporter = ExportManager(st.session_state.games_data, st.session_state.players_data)
            html_path = exporter.export_html_dashboard()
            st.success(f"Exported to: {html_path}")
            
            st.download_button(
                "⬇️ Download HTML",
                open(html_path, 'rb'),
                file_name="cu_basketball_dashboard.html",
                mime="text/html",
                use_container_width=True
            )
        
        if st.button("📈 Export to Excel", use_container_width=True):
            exporter = ExportManager(st.session_state.games_data, st.session_state.players_data)
            excel_path = exporter.export_excel()
            st.success(f"Exported to: {excel_path}")
            
            st.download_button(
                "⬇️ Download Excel",
                open(excel_path, 'rb'),
                file_name="cu_basketball_stats.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# Main content area
if not st.session_state.data_loaded:
    # Welcome screen
    st.title("🏀 Colorado Buffaloes Women's Basketball Analytics Platform")
    st.markdown("### Version 13.0 - Complete Metrics Suite")
    
    st.markdown("""
    ## Welcome to the CU Basketball Analytics System
    
    This comprehensive platform provides:
    
    ### 📊 **110+ Advanced Metrics**
    - Basic statistics (PPG, RPG, APG, etc.)
    - Advanced metrics (PER, TS%, eFG%, Usage Rate)
    - Shot selection analysis (Paint vs. Perimeter)
    - Scoring styles (Transition, Paint, Off Turnovers)
    - Assist networks and chemistry ratings
    - Quarter-by-quarter performance
    - Consistency and reliability scores
    - Clutch performance ratings
    - Situational splits (Leading, Trailing, Close games)
    - Defensive impact metrics
    - Tempo and pace analysis
    - Win Probability Added (WPA)
    - On/Off court analysis
    
    ### 🎯 **Interactive Features**
    - Real-time filtering and exploration
    - Lineup optimization engine
    - Play-by-play momentum tracking
    - Visual network diagrams
    - Comprehensive game logs
    - Player comparison tools
    
    ### 📁 **Multiple Data Sources**
    - Local XML file directories
    - Direct file uploads
    - Google Drive integration (coming soon)
    
    ### 📤 **Export Capabilities**
    - JSON data exports
    - HTML dashboard reports
    - Excel spreadsheets
    - PDF reports (coming soon)
    
    ---
    
    **👈 Get started by selecting a data source in the sidebar!**
    """)
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**🔥 Real-Time Analysis**\n\nInstantly analyze games as you add them to the system")
    
    with col2:
        st.info("**🎨 Beautiful Visualizations**\n\nInteractive charts and graphs powered by Plotly")
    
    with col3:
        st.info("**🚀 Lineup Optimizer**\n\nAI-powered recommendations for optimal player combinations")

else:
    # Main application with tabs
    st.title("🏀 CU Women's Basketball Analytics Dashboard")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "📊 Overview",
        "👥 Players", 
        "🔀 Lineups",
        "⚡ Advanced",
        "🛡️ Defense",
        "⏱️ Tempo",
        "🎯 Clutch",
        "🔄 Rotations",
        "📅 Games",
        "🎲 Play-by-Play"
    ])
    
    # Tab 1: Overview
    with tabs[0]:
        st.header("Season Overview")
        
        # Key metrics at the top
        col1, col2, col3, col4, col5 = st.columns(5)
        
        games_data = st.session_state.games_data
        total_games = len(games_data)
        wins = sum(1 for g in games_data if g.get('result') == 'W')
        losses = total_games - wins
        win_pct = wins / total_games if total_games > 0 else 0
        
        avg_score = np.mean([g.get('cu_score', 0) for g in games_data])
        avg_opp_score = np.mean([g.get('opp_score', 0) for g in games_data])
        
        with col1:
            st.metric("Record", f"{wins}-{losses}", f"{win_pct:.1%} Win Rate")
        
        with col2:
            st.metric("Avg Points", f"{avg_score:.1f}", f"+{avg_score - avg_opp_score:.1f}")
        
        with col3:
            st.metric("Opp Avg", f"{avg_opp_score:.1f}")
        
        with col4:
            st.metric("Total Games", total_games)
        
        with col5:
            st.metric("Active Players", len(st.session_state.players_data))
        
        st.markdown("---")
        
        # Scoring trend chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Scoring Trends")
            
            # Create trend dataframe
            trend_data = []
            for idx, game in enumerate(games_data):
                trend_data.append({
                    'Game': idx + 1,
                    'Date': game.get('date', f'Game {idx+1}'),
                    'CU Score': game.get('cu_score', 0),
                    'Opponent Score': game.get('opp_score', 0),
                    'Opponent': game.get('opponent', 'Unknown')
                })
            
            df_trend = pd.DataFrame(trend_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trend['Game'],
                y=df_trend['CU Score'],
                mode='lines+markers',
                name='CU Score',
                line=dict(color='#CFB87C', width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=df_trend['Game'],
                y=df_trend['Opponent Score'],
                mode='lines+markers',
                name='Opponent Score',
                line=dict(color='#565A5C', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                height=400,
                hovermode='x unified',
                xaxis_title="Game Number",
                yaxis_title="Points",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Top 5 Scorers")
            
            # Get top scorers
            players = st.session_state.players_data
            sorted_players = sorted(
                players,
                key=lambda x: x.get('metrics', {}).get('PPG', 0),
                reverse=True
            )[:5]
            
            for idx, player in enumerate(sorted_players, 1):
                metrics = player.get('metrics', {})
                ppg = metrics.get('PPG', 0)
                mpg = metrics.get('MPG', 0)
                efg = metrics.get('eFG%', 0)
                
                st.markdown(f"""
                <div class="player-card">
                    <strong>{idx}. {player['name']}</strong><br>
                    <span class="stat-highlight">{ppg:.1f} PPG</span> • 
                    {mpg:.1f} MPG • 
                    {efg:.1%} eFG%
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recent games
        st.subheader("📅 Recent Games")
        
        recent_games = games_data[-5:]
        
        for game in reversed(recent_games):
            result = game.get('result', 'L')
            cu_score = game.get('cu_score', 0)
            opp_score = game.get('opp_score', 0)
            opponent = game.get('opponent', 'Unknown')
            date = game.get('date', 'Unknown')
            
            result_color = "green" if result == 'W' else "red"
            result_emoji = "✅" if result == 'W' else "❌"
            
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                st.markdown(f"**{result_emoji} {result}**")
            
            with col2:
                st.markdown(f"vs **{opponent}**")
            
            with col3:
                st.markdown(f"**{cu_score}-{opp_score}** • {date}")
    
    # Tab 2: Players
    with tabs[1]:
        from modules.player_dashboard import render_player_dashboard
        render_player_dashboard(st.session_state.players_data, st.session_state.games_data)
    
    # Tab 3: Lineups
    with tabs[2]:
        from modules.lineup_dashboard import render_lineup_dashboard
        analyzer = LineupAnalyzer(st.session_state.games_data)
        render_lineup_dashboard(analyzer)
    
    # Tab 4: Advanced
    with tabs[3]:
        from modules.advanced_dashboard import render_advanced_dashboard
        render_advanced_dashboard(
            st.session_state.games_data,
            st.session_state.players_data,
            st.session_state.advanced_metrics
        )
    
    # Tab 5: Defense
    with tabs[4]:
        from modules.defense_dashboard import render_defense_dashboard
        render_defense_dashboard(st.session_state.players_data, st.session_state.games_data)
    
    # Tab 6: Tempo
    with tabs[5]:
        from modules.tempo_dashboard import render_tempo_dashboard
        render_tempo_dashboard(st.session_state.games_data, st.session_state.advanced_metrics)
    
    # Tab 7: Clutch
    with tabs[6]:
        from modules.clutch_dashboard import render_clutch_dashboard
        render_clutch_dashboard(st.session_state.players_data, st.session_state.games_data)
    
    # Tab 8: Rotations
    with tabs[7]:
        from modules.rotation_dashboard import render_rotation_dashboard
        render_rotation_dashboard(st.session_state.players_data, st.session_state.games_data)
    
    # Tab 9: Games
    with tabs[8]:
        from modules.game_dashboard import render_game_dashboard
        render_game_dashboard(st.session_state.games_data)
    
    # Tab 10: Play-by-Play
    with tabs[9]:
        from modules.pbp_dashboard import render_pbp_dashboard
        pbp_analyzer = PlayByPlayAnalyzer(st.session_state.games_data)
        render_pbp_dashboard(pbp_analyzer)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    <p>CU Women's Basketball Analytics Platform v13.0</p>
    <p>🏀 Go Buffs! 🏀</p>
</div>
""", unsafe_allow_html=True)
