# modules/lineup_analyzer.py
# Lineup analysis and optimization

from collections import defaultdict, Counter
from typing import List, Dict, Any
import itertools
import numpy as np

class LineupAnalyzer:
    """Analyzes and optimizes player lineup combinations"""
    
    def __init__(self, games_data):
        self.games_data = games_data
        self.lineup_stats = self._analyze_lineups()
    
    def _analyze_lineups(self):
        """Analyze lineup performance"""
        lineups = defaultdict(lambda: {
            'games': 0,
            'minutes': 0,
            'points_for': 0,
            'points_against': 0,
            'plus_minus': 0
        })
        
        for game in self.games_data:
            for lineup in game.get('lineups', []):
                if lineup.get('team') == 'H':
                    players = tuple(sorted(lineup.get('players', [])))
                    if len(players) == 5:
                        lineups[players]['games'] += 1
        
        return dict(lineups)
    
    def get_top_lineups(self, n=10):
        """Get top performing lineups"""
        sorted_lineups = sorted(
            self.lineup_stats.items(),
            key=lambda x: x[1]['games'],
            reverse=True
        )
        return sorted_lineups[:n]
    
    def get_two_player_combos(self):
        """Analyze two-player combinations"""
        combos = defaultdict(lambda: {'games': 0, 'plus_minus': 0})
        
        for lineup, stats in self.lineup_stats.items():
            for combo in itertools.combinations(lineup, 2):
                combos[combo]['games'] += stats['games']
                combos[combo]['plus_minus'] += stats.get('plus_minus', 0)
        
        return dict(combos)
    
    def optimize_lineup(self, situation='closing'):
        """Optimize lineup for specific situation"""
        # Placeholder - would implement optimization algorithm
        return ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5']
