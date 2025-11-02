# modules/data_loader.py
# Handles loading and parsing XML game files

import xml.etree.ElementTree as ET
from lxml import etree as LET
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import io
import os

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
        
        # Try multiple possible path locations
        possible_paths = [
            Path(self.directory),
            Path(f"/mount/src/cu-basketball-analytics/{self.directory}"),
            Path(f"./{self.directory}"),
            Path(f"/app/cu-basketball-analytics/{self.directory}"),
            Path(os.path.join(os.getcwd(), self.directory))
        ]
        
        path = None
        for test_path in possible_paths:
            if test_path.exists() and test_path.is_dir():
                path = test_path
                print(f"✅ Found directory at: {path}")
                break
        
        if path is None:
            print(f"❌ Directory not found. Tried: {[str(p) for p in possible_paths]}")
            return []
        
        games = []
        xml_files = sorted(path.glob("*.xml"))
        
        print(f"✅ Found {len(xml_files)} XML files")
        
        for xml_file in xml_files:
            try:
                game_data = self.parse_game_file(str(xml_file))
                if game_data:
                    games.append(game_data)
                    print(f"✅ Loaded: {xml_file.name}")
            except Exception as e:
                print(f"❌ Error parsing {xml_file.name}: {str(e)}")
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
