# modules/export_manager.py
# Export functionality for data and reports

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class ExportManager:
    """Handles data export in multiple formats"""
    
    def __init__(self, games_data, players_data):
        self.games_data = games_data
        self.players_data = players_data
        self.output_dir = Path("/home/claude/output")
        self.output_dir.mkdir(exist_ok=True)
    
    def export_json(self):
        """Export complete data to JSON"""
        export_data = {
            'generated': datetime.now().isoformat(),
            'games': self.games_data,
            'players': self.players_data,
            'summary': {
                'total_games': len(self.games_data),
                'total_players': len(self.players_data)
            }
        }
        
        filepath = self.output_dir / 'cu_basketball_data.json'
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(filepath)
    
    def export_excel(self):
        """Export data to Excel workbook"""
        filepath = self.output_dir / 'cu_basketball_stats.xlsx'
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Player stats sheet
            player_data = []
            for player in self.players_data:
                row = {'Name': player['name'], 'Position': player['position']}
                row.update(player.get('metrics', {}))
                player_data.append(row)
            
            df_players = pd.DataFrame(player_data)
            df_players.to_excel(writer, sheet_name='Player Stats', index=False)
            
            # Game results sheet
            game_data = []
            for game in self.games_data:
                game_data.append({
                    'Date': game.get('date'),
                    'Opponent': game.get('opponent'),
                    'Result': game.get('result'),
                    'CU Score': game.get('cu_score'),
                    'Opp Score': game.get('opp_score')
                })
            
            df_games = pd.DataFrame(game_data)
            df_games.to_excel(writer, sheet_name='Games', index=False)
        
        return str(filepath)
    
    def export_html_dashboard(self):
        """Export static HTML dashboard"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CU Basketball Analytics</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #000; color: #FFD700; padding: 20px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                          background: #f0f0f0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CU Women's Basketball Analytics</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <h2>Season Summary</h2>
            <div class="metric">
                <strong>Total Games:</strong> {len(self.games_data)}
            </div>
            <div class="metric">
                <strong>Total Players:</strong> {len(self.players_data)}
            </div>
        </body>
        </html>
        """
        
        filepath = self.output_dir / 'cu_basketball_dashboard.html'
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return str(filepath)
