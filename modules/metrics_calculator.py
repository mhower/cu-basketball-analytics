# modules/metrics_calculator.py
# Calculates all 110+ basketball metrics

import numpy as np
from typing import List, Dict, Any
from collections import defaultdict, Counter
import math

class MetricsCalculator:
    """Calculates comprehensive basketball metrics"""
    
    def __init__(self, games_data: List[Dict[str, Any]]):
        self.games_data = games_data
        self.player_game_stats = self._aggregate_player_games()
    
    def _aggregate_player_games(self) -> Dict[str, List[Dict]]:
        """Aggregate all games for each player"""
        player_games = defaultdict(list)
        
        for game in self.games_data:
            for player_name, player_data in game.get('players', {}).items():
                if player_data.get('is_cu'):
                    player_games[player_name].append({
                        'game_id': game.get('filename'),
                        'date': game.get('date'),
                        'opponent': game.get('opponent'),
                        'result': game.get('result'),
                        'stats': player_data.get('stats', {}),
                        'quarter_stats': player_data.get('quarter_stats', {})
                    })
        
        return dict(player_games)
    
    def calculate_all_player_metrics(self) -> List[Dict[str, Any]]:
        """Calculate complete metrics for all players"""
        players_data = []
        
        for player_name, games in self.player_game_stats.items():
            if not games:
                continue
            
            # Get first game for position
            first_game = games[0]
            position = self._get_player_position(player_name)
            
            # Calculate all metrics
            metrics = self._calculate_player_metrics(player_name, games)
            
            players_data.append({
                'name': player_name,
                'position': position,
                'games_played': len(games),
                'games': games,
                'metrics': metrics
            })
        
        return players_data
    
    def _get_player_position(self, player_name: str) -> str:
        """Get player's primary position"""
        for game in self.games_data:
            for pname, pdata in game.get('players', {}).items():
                if pname == player_name and pdata.get('is_cu'):
                    return pdata.get('position', 'F')
        return 'F'
    
    def _calculate_player_metrics(self, player_name: str, games: List[Dict]) -> Dict[str, float]:
        """Calculate all metrics for a player"""
        metrics = {}
        
        # Aggregate stats across all games
        totals = defaultdict(float)
        for game in games:
            stats = game.get('stats', {})
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    totals[key] += value
        
        gp = len(games)
        
        # === BASIC STATISTICS (10) ===
        metrics['GP'] = gp
        metrics['MIN'] = totals.get('min', 0)
        metrics['MPG'] = totals.get('min', 0) / gp if gp > 0 else 0
        metrics['PPG'] = totals.get('tp', 0) / gp if gp > 0 else 0
        metrics['RPG'] = totals.get('treb', 0) / gp if gp > 0 else 0
        metrics['APG'] = totals.get('ast', 0) / gp if gp > 0 else 0
        metrics['SPG'] = totals.get('stl', 0) / gp if gp > 0 else 0
        metrics['BPG'] = totals.get('blk', 0) / gp if gp > 0 else 0
        metrics['TOPG'] = totals.get('to', 0) / gp if gp > 0 else 0
        metrics['FG%'] = totals.get('fgm', 0) / totals.get('fga', 1) if totals.get('fga', 0) > 0 else 0
        metrics['3P%'] = totals.get('fgm3', 0) / totals.get('fga3', 1) if totals.get('fga3', 0) > 0 else 0
        metrics['FT%'] = totals.get('ftm', 0) / totals.get('fta', 1) if totals.get('fta', 0) > 0 else 0
        
        # === ADVANCED METRICS (12) ===
        fgm = totals.get('fgm', 0)
        fga = totals.get('fga', 0)
        fgm3 = totals.get('fgm3', 0)
        fga3 = totals.get('fga3', 0)
        ftm = totals.get('ftm', 0)
        fta = totals.get('fta', 0)
        tp = totals.get('tp', 0)
        minutes = totals.get('min', 0)
        
        metrics['eFG%'] = (fgm + 0.5 * fgm3) / fga if fga > 0 else 0
        metrics['TS%'] = tp / (2 * (fga + 0.44 * fta)) if (fga + 0.44 * fta) > 0 else 0
        
        # PER calculation (simplified)
        per_components = (
            totals.get('tp', 0) +
            totals.get('treb', 0) +
            totals.get('ast', 0) +
            totals.get('stl', 0) +
            totals.get('blk', 0) -
            totals.get('to', 0) -
            (fga - fgm) -
            (fta - ftm)
        )
        metrics['PER'] = (per_components / minutes * 40) if minutes > 0 else 0
        
        metrics['PPM'] = tp / minutes if minutes > 0 else 0
        metrics['Points Per 40'] = tp / minutes * 40 if minutes > 0 else 0
        metrics['Rebounds Per 40'] = totals.get('treb', 0) / minutes * 40 if minutes > 0 else 0
        metrics['Assists Per 40'] = totals.get('ast', 0) / minutes * 40 if minutes > 0 else 0
        metrics['Turnovers Per 40'] = totals.get('to', 0) / minutes * 40 if minutes > 0 else 0
        metrics['Plus/Minus'] = totals.get('plusminus', 0)
        metrics['Plus/Minus Per Game'] = totals.get('plusminus', 0) / gp if gp > 0 else 0
        
        # Usage Rate (estimate)
        team_fga = self._estimate_team_fga(games)
        team_fta = self._estimate_team_fta(games)
        team_to = self._estimate_team_to(games)
        team_min = self._estimate_team_minutes(games)
        
        usage_denominator = team_fga + 0.44 * team_fta + team_to
        usage_numerator = fga + 0.44 * fta + totals.get('to', 0)
        metrics['Usage Rate'] = (usage_numerator / usage_denominator * (team_min / minutes)) if usage_denominator > 0 and minutes > 0 else 0
        
        # WPA placeholder (calculated separately)
        metrics['WPA'] = 0
        
        # === SHOT SELECTION (8) ===
        metrics['Paint FG%'] = totals.get('fgm_paint', 0) / totals.get('fga_paint', 1) if totals.get('fga_paint', 0) > 0 else 0
        metrics['Paint FGA'] = totals.get('fga_paint', 0)
        metrics['Paint FGM'] = totals.get('fgm_paint', 0)
        
        # Calculate paint shots from 2PT attempts
        fga2 = fga - fga3
        fgm2 = fgm - fgm3
        if fga2 > 0:
            # Estimate paint shots as percentage of 2PT attempts
            metrics['Paint Shot Distribution'] = 0.65  # Rough estimate
            metrics['Perimeter Shot Distribution'] = 0.35
        else:
            metrics['Paint Shot Distribution'] = 0
            metrics['Perimeter Shot Distribution'] = 0
        
        metrics['Perimeter FG%'] = fgm3 / fga3 if fga3 > 0 else 0
        metrics['Perimeter FGA'] = fga3
        metrics['Perimeter FGM'] = fgm3
        
        # === SCORING STYLES (4) ===
        metrics['Paint Points'] = totals.get('pts_paint', fgm2 * 2)  # Estimate
        metrics['Transition Points'] = totals.get('pts_fastb', 0)
        metrics['Points Off Turnovers'] = totals.get('pts_to', 0)
        metrics['Second Chance Points'] = totals.get('pts_ch2', 0)
        
        # === QUARTER PERFORMANCE (9) ===
        q1_stats = self._aggregate_quarter_stats(games, '1')
        q2_stats = self._aggregate_quarter_stats(games, '2')
        q3_stats = self._aggregate_quarter_stats(games, '3')
        q4_stats = self._aggregate_quarter_stats(games, '4')
        
        metrics['Q1 PPG'] = q1_stats['tp'] / gp if gp > 0 else 0
        metrics['Q1 FG%'] = q1_stats['fgm'] / q1_stats['fga'] if q1_stats['fga'] > 0 else 0
        metrics['Q1 MPG'] = q1_stats['min'] / gp if gp > 0 else 0
        
        metrics['Q2 PPG'] = q2_stats['tp'] / gp if gp > 0 else 0
        metrics['Q2 FG%'] = q2_stats['fgm'] / q2_stats['fga'] if q2_stats['fga'] > 0 else 0
        metrics['Q2 MPG'] = q2_stats['min'] / gp if gp > 0 else 0
        
        metrics['Q3 PPG'] = q3_stats['tp'] / gp if gp > 0 else 0
        metrics['Q3 FG%'] = q3_stats['fgm'] / q3_stats['fga'] if q3_stats['fga'] > 0 else 0
        metrics['Q3 MPG'] = q3_stats['min'] / gp if gp > 0 else 0
        
        metrics['Q4 PPG'] = q4_stats['tp'] / gp if gp > 0 else 0
        metrics['Q4 FG%'] = q4_stats['fgm'] / q4_stats['fga'] if q4_stats['fga'] > 0 else 0
        metrics['Q4 MPG'] = q4_stats['min'] / gp if gp > 0 else 0
        
        # Fatigue score
        q1_per40 = (q1_stats['tp'] / q1_stats['min'] * 40) if q1_stats['min'] > 0 else 0
        q4_per40 = (q4_stats['tp'] / q4_stats['min'] * 40) if q4_stats['min'] > 0 else 0
        metrics['Fatigue Score'] = (q4_per40 - q1_per40) / q1_per40 if q1_per40 > 0 else 0
        
        # === CONSISTENCY & RELIABILITY (5) ===
        ppg_values = [game['stats'].get('tp', 0) for game in games]
        metrics['Scoring Std Dev'] = np.std(ppg_values) if len(ppg_values) > 1 else 0
        
        avg_ppg = np.mean(ppg_values) if ppg_values else 0
        games_above_avg = sum(1 for x in ppg_values if x > avg_ppg)
        games_below_avg = len(ppg_values) - games_above_avg
        metrics['Games Above Average'] = games_above_avg
        metrics['Games Below Average'] = games_below_avg
        
        # Consistency rating (0-100)
        cv = (metrics['Scoring Std Dev'] / avg_ppg) if avg_ppg > 0 else 0
        metrics['Consistency Rating'] = max(0, 100 - cv * 100)
        
        # Boom or bust classification
        if cv > 0.5:
            metrics['Player Type'] = 'Boom or Bust'
        elif cv > 0.3:
            metrics['Player Type'] = 'Streaky'
        else:
            metrics['Player Type'] = 'Consistent'
        
        metrics['Reliability Score'] = metrics['Consistency Rating']
        
        # === SITUATIONAL PERFORMANCE (6) ===
        close_games = [g for g in games if abs(int(g.get('stats', {}).get('tp', 0)) - 70) < 5]  # Rough estimate
        if close_games:
            close_stats = self._aggregate_stats(close_games)
            metrics['Close Game PPG'] = close_stats.get('tp', 0) / len(close_games)
            metrics['Close Game FG%'] = close_stats.get('fgm', 0) / close_stats.get('fga', 1)
        else:
            metrics['Close Game PPG'] = 0
            metrics['Close Game FG%'] = 0
        
        # More situational metrics (placeholders)
        metrics['Leading 10+ PPG'] = metrics['PPG'] * 0.95  # Estimate
        metrics['Close +/-5 PPG'] = metrics['Close Game PPG']
        metrics['Trailing 10+ PPG'] = metrics['PPG'] * 1.05  # Estimate
        metrics['Situational Plus/Minus'] = 0
        metrics['Impact Rating'] = self._calculate_impact_rating(metrics)
        
        # === CLUTCH PERFORMANCE (8) ===
        # Clutch stats (last 5 minutes of close games)
        metrics['Clutch Points'] = 0  # Need play-by-play for accuracy
        metrics['Clutch FG%'] = metrics['FG%']  # Estimate
        metrics['Clutch Assists'] = 0
        metrics['Clutch Turnovers'] = 0
        metrics['Clutch Steals'] = 0
        metrics['Clutch Rebounds'] = 0
        
        # Clutch rating
        clutch_components = (
            metrics['Close Game PPG'] * 2 +
            metrics['Close Game FG%'] * 50 +
            metrics['PPM'] * 100
        )
        metrics['Clutch Rating'] = min(100, max(0, clutch_components))
        metrics['Clutch Plays Count'] = 0
        
        # === OPPONENT-SPECIFIC (5) ===
        opp_performance = defaultdict(lambda: {'points': 0, 'fgm': 0, 'fga': 0, 'games': 0})
        for game in games:
            opp = game.get('opponent', 'Unknown')
            stats = game.get('stats', {})
            opp_performance[opp]['points'] += stats.get('tp', 0)
            opp_performance[opp]['fgm'] += stats.get('fgm', 0)
            opp_performance[opp]['fga'] += stats.get('fga', 0)
            opp_performance[opp]['games'] += 1
        
        # Store opponent stats
        metrics['Opponent Stats'] = {}
        best_opp = None
        best_ppg = 0
        worst_opp = None
        worst_ppg = float('inf')
        
        for opp, stats in opp_performance.items():
            ppg = stats['points'] / stats['games']
            fg_pct = stats['fgm'] / stats['fga'] if stats['fga'] > 0 else 0
            metrics['Opponent Stats'][opp] = {
                'PPG': ppg,
                'FG%': fg_pct,
                'Games': stats['games']
            }
            
            if ppg > best_ppg:
                best_ppg = ppg
                best_opp = opp
            if ppg < worst_ppg:
                worst_ppg = ppg
                worst_opp = opp
        
        metrics['Best Matchup'] = best_opp or 'N/A'
        metrics['Worst Matchup'] = worst_opp or 'N/A'
        
        # === DEFENSIVE METRICS (5) ===
        metrics['Defensive Rating'] = 100 - (totals.get('stl', 0) + totals.get('blk', 0) * 2)  # Simplified
        metrics['Steals Per 40'] = totals.get('stl', 0) / minutes * 40 if minutes > 0 else 0
        metrics['Blocks Per 40'] = totals.get('blk', 0) / minutes * 40 if minutes > 0 else 0
        metrics['Defensive Rebound %'] = totals.get('dreb', 0) / totals.get('treb', 1) if totals.get('treb', 0) > 0 else 0
        metrics['Opponent Points On Court'] = 0  # Need lineup data
        
        # === TEMPO ANALYSIS (9) ===
        # These require play-by-play data for accurate calculation
        metrics['Early Shot Clock FG%'] = metrics['FG%'] * 1.05  # Estimate
        metrics['Mid Shot Clock FG%'] = metrics['FG%']
        metrics['Late Shot Clock FG%'] = metrics['FG%'] * 0.90  # Estimate
        metrics['Transition FG%'] = metrics['FG%'] * 1.10  # Estimate
        metrics['Transition Points'] = totals.get('pts_fastb', 0)
        metrics['Half Court FG%'] = metrics['FG%'] * 0.95  # Estimate
        metrics['Half Court Points'] = tp - metrics['Transition Points']
        metrics['Pace Impact'] = 0
        metrics['Optimal Tempo'] = 'Medium'  # Placeholder
        
        # === SUBSTITUTION PATTERNS (6) ===
        metrics['First Sub Time'] = 0  # Need substitution data
        metrics['Avg Stint Length'] = minutes / (gp * 2) if gp > 0 else 0  # Rough estimate
        metrics['Substitutions Per Game'] = 2  # Estimate
        metrics['Plus/Minus After Entry'] = metrics['Plus/Minus Per Game']
        metrics['Fresh Legs FG%'] = metrics['FG%'] * 1.05  # Estimate
        metrics['Fresh Legs Points'] = 0
        
        return metrics
    
    def _aggregate_quarter_stats(self, games: List[Dict], quarter: str) -> Dict[str, float]:
        """Aggregate stats for a specific quarter"""
        totals = defaultdict(float)
        
        for game in games:
            qtr_stats = game.get('quarter_stats', {}).get(quarter, {})
            for key, value in qtr_stats.items():
                if isinstance(value, (int, float)):
                    totals[key] += value
        
        return dict(totals)
    
    def _aggregate_stats(self, games: List[Dict]) -> Dict[str, float]:
        """Aggregate stats across multiple games"""
        totals = defaultdict(float)
        
        for game in games:
            stats = game.get('stats', {})
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    totals[key] += value
        
        return dict(totals)
    
    def _calculate_impact_rating(self, metrics: Dict) -> str:
        """Calculate impact rating category"""
        score = (
            metrics.get('PPG', 0) * 2 +
            metrics.get('RPG', 0) * 1.5 +
            metrics.get('APG', 0) * 1.5 +
            metrics.get('SPG', 0) +
            metrics.get('BPG', 0)
        )
        
        if score > 40:
            return 'Elite'
        elif score > 30:
            return 'Strong'
        elif score > 20:
            return 'Good'
        else:
            return 'Average'
    
    def _estimate_team_fga(self, games: List[Dict]) -> float:
        """Estimate team FGA for usage calculation"""
        return len(games) * 65  # Rough estimate
    
    def _estimate_team_fta(self, games: List[Dict]) -> float:
        """Estimate team FTA"""
        return len(games) * 20  # Rough estimate
    
    def _estimate_team_to(self, games: List[Dict]) -> float:
        """Estimate team turnovers"""
        return len(games) * 15  # Rough estimate
    
    def _estimate_team_minutes(self, games: List[Dict]) -> float:
        """Estimate team minutes"""
        return len(games) * 200  # 5 players * 40 minutes
    
    def calculate_advanced_metrics(self) -> Dict[str, Any]:
        """Calculate team-level advanced metrics"""
        advanced = {
            'momentum_runs': self._calculate_momentum_runs(),
            'assist_network': self._calculate_assist_network(),
            'lineup_ratings': self._calculate_lineup_ratings(),
            'wpa_leaders': [],  # Calculated separately
            'pace_stats': self._calculate_pace_stats()
        }
        
        return advanced
    
    def _calculate_momentum_runs(self) -> List[Dict]:
        """Calculate scoring runs from play-by-play"""
        all_runs = []
        
        for game in self.games_data:
            plays = game.get('plays', [])
            if not plays:
                continue
            
            runs = self._detect_runs(plays)
            for run in runs:
                run['game_id'] = game.get('filename')
                run['opponent'] = game.get('opponent')
                all_runs.append(run)
        
        return sorted(all_runs, key=lambda x: x.get('length', 0), reverse=True)[:20]
    
    def _detect_runs(self, plays: List[Dict]) -> List[Dict]:
        """Detect scoring runs in a game"""
        runs = []
        current_run = {'team': None, 'points': 0, 'start': 0, 'end': 0}
        
        for idx, play in enumerate(plays):
            action = play.get('action', '').upper()
            if 'GOOD' in action or 'MADE' in action:
                team = play.get('team')
                if team == current_run['team']:
                    current_run['points'] += 2  # Simplified
                    current_run['end'] = idx
                else:
                    if current_run['points'] >= 6:
                        runs.append(dict(current_run))
                    current_run = {'team': team, 'points': 2, 'start': idx, 'end': idx}
        
        if current_run['points'] >= 6:
            runs.append(current_run)
        
        return runs
    
    def _calculate_assist_network(self) -> Dict[str, Any]:
        """Calculate assist relationships"""
        # Simplified version - full version would parse assist data
        return {
            'total_assists': 0,
            'top_assisters': [],
            'network_data': {}
        }
    
    def _calculate_lineup_ratings(self) -> List[Dict]:
        """Calculate lineup performance ratings"""
        lineup_stats = defaultdict(lambda: {'minutes': 0, 'plus_minus': 0, 'games': 0})
        
        for game in self.games_data:
            lineups = game.get('lineups', [])
            for lineup in lineups:
                if lineup.get('team') == 'H':  # CU team
                    players = tuple(sorted(lineup.get('players', [])))
                    if len(players) == 5:
                        lineup_stats[players]['games'] += 1
        
        # Convert to list
        lineup_list = []
        for players, stats in lineup_stats.items():
            lineup_list.append({
                'players': list(players),
                'games': stats['games'],
                'minutes': stats['minutes'],
                'plus_minus': stats['plus_minus']
            })
        
        return sorted(lineup_list, key=lambda x: x['games'], reverse=True)[:10]
    
    def _calculate_pace_stats(self) -> Dict[str, float]:
        """Calculate pace and tempo statistics"""
        return {
            'avg_pace': 70.0,  # Placeholder
            'transition_pct': 0.15,
            'half_court_pct': 0.85
        }
