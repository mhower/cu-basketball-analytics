# modules/play_analyzer.py
# Play-by-play analysis

from collections import defaultdict, Counter
from typing import List, Dict, Any

class PlayByPlayAnalyzer:
    """Analyzes play-by-play data"""
    
    def __init__(self, games_data):
        self.games_data = games_data
        self.all_plays = self._collect_all_plays()
    
    def _collect_all_plays(self):
        """Collect all plays from all games"""
        all_plays = []
        for game in self.games_data:
            plays = game.get('plays', [])
            for play in plays:
                play['game_id'] = game.get('filename')
                play['opponent'] = game.get('opponent')
                all_plays.append(play)
        return all_plays
    
    def get_scoring_plays(self):
        """Get all scoring plays"""
        scoring = []
        for play in self.all_plays:
            action = play.get('action', '').upper()
            if 'GOOD' in action or 'MADE' in action:
                scoring.append(play)
        return scoring
    
    def analyze_runs(self):
        """Analyze scoring runs"""
        runs_by_game = {}
        for game in self.games_data:
            plays = game.get('plays', [])
            runs = self._detect_runs_in_game(plays)
            runs_by_game[game.get('filename')] = runs
        return runs_by_game
    
    def _detect_runs_in_game(self, plays):
        """Detect runs within a single game"""
        runs = []
        current_team = None
        current_points = 0
        start_idx = 0
        
        for idx, play in enumerate(plays):
            action = play.get('action', '').upper()
            if 'GOOD' in action or 'MADE' in action:
                team = play.get('team')
                if team == current_team:
                    current_points += self._get_points_for_play(play)
                else:
                    if current_points >= 6:
                        runs.append({
                            'team': current_team,
                            'points': current_points,
                            'start': start_idx,
                            'end': idx - 1
                        })
                    current_team = team
                    current_points = self._get_points_for_play(play)
                    start_idx = idx
        
        return runs
    
    def _get_points_for_play(self, play):
        """Determine points scored on a play"""
        type_str = str(play.get('type', '')).upper()
        action = str(play.get('action', '')).upper()
        
        if '3PT' in type_str or '3PTR' in type_str:
            return 3
        elif 'FT' in type_str or 'FREE THROW' in action:
            return 1
        else:
            return 2
    
    def get_momentum_swings(self):
        """Identify momentum swings"""
        swings = []
        for game in self.games_data:
            plays = game.get('plays', [])
            prev_score_diff = 0
            
            for play in plays:
                hscore = play.get('hscore', 0)
                vscore = play.get('vscore', 0)
                diff = hscore - vscore
                
                if abs(diff - prev_score_diff) >= 10:
                    swings.append({
                        'game': game.get('filename'),
                        'time': play.get('time'),
                        'period': play.get('period'),
                        'swing': abs(diff - prev_score_diff)
                    })
                
                prev_score_diff = diff
        
        return sorted(swings, key=lambda x: x['swing'], reverse=True)[:20]
