# modules/data_loader.py
# Handles loading and parsing XML game files

import xml.etree.ElementTree as ET
from lxml import etree as LET
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import io

class GameDataLoader:
    """Loads and parses XML game data files"""
    
    def __init__(self, directory: Optional[str] = None):
        self.directory = directory
        self.cu_roster = [
            "Sanders, Kennedy", "Teder, Johanna", "Masogayo, Jade",
            "Garzon, Lior", "Diew, Nyamer", "Johnson, Ayianna",
            "Wetta, Kindyll", "Beh, Isis", "Formann, Sara"
        ]
    
    def load_all_games(self) -> List[Dict[str, Any]]:
        """Load all XML files from directory"""
        if not self.directory:
            return []
        
        path = Path(self.directory)
        if not path.exists():
            raise ValueError(f"Directory not found: {self.directory}")
        
        games = []
        xml_files = sorted(path.glob("*.xml"))
        
        for xml_file in xml_files:
            try:
                game_data = self.parse_game_file(str(xml_file))
                if game_data:
                    games.append(game_data)
            except Exception as e:
                print(f"Error parsing {xml_file.name}: {str(e)}")
                continue
        
        return games
    
    def load_from_uploads(self, uploaded_files) -> List[Dict[str, Any]]:
        """Load games from uploaded file objects"""
        games = []
        
        for uploaded_file in uploaded_files:
            try:
                content = uploaded_file.read()
                game_data = self.parse_game_content(content, uploaded_file.name)
                if game_data:
                    games.append(game_data)
            except Exception as e:
                print(f"Error parsing {uploaded_file.name}: {str(e)}")
                continue
        
        return games
    
    def parse_game_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a single XML game file"""
        with open(filepath, 'rb') as f:
            content = f.read()
        
        filename = Path(filepath).name
        return self.parse_game_content(content, filename)
    
    def parse_game_content(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse XML content into game data structure"""
        parser = LET.XMLParser(recover=True)
        root = LET.fromstring(content, parser)
        
        # Extract basic game info
        game_data = {
            'filename': filename,
            'file_id': filename.replace('.xml', ''),
            'date': self._extract_date(root),
            'date_obj': None,
            'venue': self._extract_venue(root),
            'teams': {},
            'players': {},
            'plays': [],
            'lineups': [],
            'cu_score': 0,
            'opp_score': 0,
            'opponent': 'Unknown',
            'result': 'L',
            'home_away': 'Home'
        }
        
        # Parse date
        if game_data['date']:
            game_data['date_obj'] = self._parse_date(game_data['date'])
        
        # Extract teams
        teams = self._extract_teams(root)
        game_data['teams'] = teams
        
        # Determine which team is CU
        cu_team = None
        opp_team = None
        
        for team_id, team_info in teams.items():
            team_name = team_info.get('name', '').upper()
            if 'COLORADO' in team_name or 'COL' in team_name:
                cu_team = team_id
            else:
                opp_team = team_id
        
        if not cu_team and teams:
            # Default to first team if CU not found
            team_ids = list(teams.keys())
            cu_team = team_ids[0]
            opp_team = team_ids[1] if len(team_ids) > 1 else None
        
        # Extract scores
        if cu_team and cu_team in teams:
            game_data['cu_score'] = teams[cu_team].get('score', 0)
        if opp_team and opp_team in teams:
            game_data['opp_score'] = teams[opp_team].get('score', 0)
            game_data['opponent'] = teams[opp_team].get('name', 'Unknown')
        
        # Determine result
        game_data['result'] = 'W' if game_data['cu_score'] > game_data['opp_score'] else 'L'
        
        # Determine home/away
        if cu_team == 'H':
            game_data['home_away'] = 'Home'
        elif cu_team == 'V':
            game_data['home_away'] = 'Away'
        
        # Extract players
        game_data['players'] = self._extract_all_players(root, teams, cu_team)
        
        # Extract play-by-play
        game_data['plays'] = self._extract_plays(root)
        
        # Track lineups from plays
        game_data['lineups'] = self._track_lineups(game_data['plays'], game_data['players'])
        
        return game_data
    
    def _extract_date(self, root) -> str:
        """Extract game date from XML"""
        # Try multiple locations
        venue = root.find('.//venue')
        if venue is not None:
            date = venue.get('date') or venue.get('gametime')
            if date:
                return date
        
        # Try other locations
        for elem in root.iter():
            if 'date' in elem.attrib:
                return elem.attrib['date']
        
        return "Unknown"
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        formats = [
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%m/%d/%y",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    def _extract_venue(self, root) -> str:
        """Extract venue information"""
        venue = root.find('.//venue')
        if venue is not None:
            location = venue.get('location')
            if location:
                return location
        
        return "Unknown Venue"
    
    def _extract_teams(self, root) -> Dict[str, Dict[str, Any]]:
        """Extract team information"""
        teams = {}
        
        for team in root.findall('.//team'):
            team_id = team.get('vh') or team.get('id') or team.get('code')
            if not team_id:
                continue
            
            # Get team name
            name = team.get('name') or team.get('teamname') or 'Unknown'
            
            # Get linescore
            linescore_elem = team.find('.//linescore')
            score = 0
            quarters = []
            
            if linescore_elem is not None:
                score = int(linescore_elem.get('score') or 0)
                
                for lineprd in linescore_elem.findall('.//lineprd'):
                    period = lineprd.get('prd') or lineprd.get('period')
                    prd_score = int(lineprd.get('score') or 0)
                    quarters.append({'period': period, 'score': prd_score})
            
            # Get totals
            totals = {}
            totals_elem = team.find('.//totals/stats') or team.find('.//totals')
            if totals_elem is not None:
                for key, value in totals_elem.attrib.items():
                    try:
                        totals[key] = float(value) if '.' in value else int(value)
                    except:
                        totals[key] = value
            
            teams[team_id] = {
                'id': team_id,
                'name': name,
                'score': score,
                'quarters': quarters,
                'totals': totals
            }
        
        return teams
    
    def _extract_all_players(self, root, teams: Dict, cu_team_id: str) -> Dict[str, Dict[str, Any]]:
        """Extract all player statistics"""
        players = {}
        
        for team_id, team_info in teams.items():
            team = root.find(f".//team[@vh='{team_id}']") or root.find(f".//team[@id='{team_id}']")
            if team is None:
                continue
            
            is_cu = (team_id == cu_team_id)
            
            for player_elem in team.findall('.//player'):
                player_data = self._extract_player_stats(player_elem, team_id, is_cu)
                if player_data:
                    player_name = player_data['name']
                    players[player_name] = player_data
        
        return players
    
    def _extract_player_stats(self, player_elem, team_id: str, is_cu: bool) -> Dict[str, Any]:
        """Extract statistics for a single player"""
        # Basic info
        name = player_elem.get('name') or player_elem.get('player')
        if not name or name.upper() == 'TEAM':
            return None
        
        # Clean up name
        name = self._normalize_name(name)
        
        position = player_elem.get('pos') or player_elem.get('position') or 'F'
        uni = player_elem.get('uni') or ''
        
        player_data = {
            'name': name,
            'position': position,
            'uniform': uni,
            'team': team_id,
            'is_cu': is_cu,
            'stats': {},
            'quarter_stats': {}
        }
        
        # Extract main stats
        stats_elem = player_elem.find('.//stats')
        if stats_elem is not None:
            for key, value in stats_elem.attrib.items():
                try:
                    player_data['stats'][key] = float(value) if '.' in str(value) else int(value)
                except:
                    player_data['stats'][key] = value
        
        # Extract quarter stats
        for qtr_elem in player_elem.findall('.//statsbyprd'):
            period = qtr_elem.get('prd') or qtr_elem.get('period')
            if period:
                qtr_stats = {}
                for key, value in qtr_elem.attrib.items():
                    if key not in ['prd', 'period']:
                        try:
                            qtr_stats[key] = float(value) if '.' in str(value) else int(value)
                        except:
                            qtr_stats[key] = value
                
                player_data['quarter_stats'][period] = qtr_stats
        
        return player_data
    
    def _normalize_name(self, name: str) -> str:
        """Normalize player name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Handle "Last, First" format
        if ',' in name:
            parts = name.split(',')
            name = f"{parts[1].strip()} {parts[0].strip()}"
        
        return name.strip()
    
    def _extract_plays(self, root) -> List[Dict[str, Any]]:
        """Extract play-by-play data"""
        plays = []
        
        # Find plays section
        plays_section = root.find('.//plays') or root.find('.//playbyplay')
        if plays_section is None:
            return plays
        
        play_id = 0
        
        for period in plays_section.findall('.//period'):
            period_num = period.get('number') or period.get('prd') or '1'
            
            for play_elem in period.findall('.//play'):
                play_data = self._parse_play(play_elem, period_num, play_id)
                if play_data:
                    plays.append(play_data)
                    play_id += 1
        
        # If no periods, look for direct play elements
        if not plays:
            for play_elem in plays_section.findall('.//play'):
                play_data = self._parse_play(play_elem, '1', play_id)
                if play_data:
                    plays.append(play_data)
                    play_id += 1
        
        return plays
    
    def _parse_play(self, play_elem, period: str, play_id: int) -> Dict[str, Any]:
        """Parse a single play element"""
        play_data = {
            'id': play_id,
            'period': period,
            'time': play_elem.get('time') or play_elem.get('clock') or '10:00',
            'team': play_elem.get('vh') or play_elem.get('team'),
            'player': play_elem.get('checkname') or play_elem.get('player'),
            'action': play_elem.get('action'),
            'type': play_elem.get('type'),
            'hscore': int(play_elem.get('hscore') or 0),
            'vscore': int(play_elem.get('vscore') or 0),
            'text': play_elem.text or ''
        }
        
        # Extract additional attributes
        for key, value in play_elem.attrib.items():
            if key not in play_data:
                play_data[key] = value
        
        return play_data
    
    def _track_lineups(self, plays: List[Dict], players: Dict) -> List[Dict[str, Any]]:
        """Track lineup changes from play-by-play"""
        lineups = []
        
        if not plays:
            return lineups
        
        # Initialize lineups
        current_lineup = {'H': set(), 'V': set()}
        
        # Try to get starters
        cu_starters = [p['name'] for p in players.values() if p.get('is_cu') and p.get('stats', {}).get('gs') == 1]
        if cu_starters and len(cu_starters) <= 5:
            current_lineup['H'] = set(cu_starters)
        
        for play in plays:
            action = play.get('action', '').upper()
            play_type = play.get('type', '').upper()
            
            if 'SUB' in action:
                player = play.get('player')
                team = play.get('team', 'H')
                
                if player:
                    player = self._normalize_name(player)
                    
                    if 'IN' in play_type or 'ENTERS' in action:
                        current_lineup[team].add(player)
                    elif 'OUT' in play_type or 'LEAVES' in action:
                        current_lineup[team].discard(player)
                    
                    # Record lineup snapshot when we have 5 players
                    if len(current_lineup[team]) == 5:
                        lineups.append({
                            'time': play.get('time'),
                            'period': play.get('period'),
                            'team': team,
                            'players': list(current_lineup[team]),
                            'score': {'H': play.get('hscore', 0), 'V': play.get('vscore', 0)}
                        })
        
        return lineups
