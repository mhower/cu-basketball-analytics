# modules/game_dashboard.py
import streamlit as st

def render_game_dashboard(games_data):
    st.header("📅 Game-by-Game Analysis")
    
    for game in reversed(games_data):
        with st.expander(
            f"{game.get('date', 'Unknown')} - {game.get('result', 'L')} vs {game.get('opponent', 'Unknown')} "
            f"({game.get('cu_score', 0)}-{game.get('opp_score', 0)})"
        ):
            st.write(f"**Venue:** {game.get('venue', 'Unknown')}")
            st.write(f"**Location:** {game.get('home_away', 'Unknown')}")
            
            # Quarter scores
            teams = game.get('teams', {})
            for team_id, team_info in teams.items():
                quarters = team_info.get('quarters', [])
                if quarters:
                    qtr_scores = [q['score'] for q in quarters]
                    st.write(f"{team_info['name']}: {' | '.join(map(str, qtr_scores))}")
