
import pandas as pd
from src.services.player_service import player_defensive_capacity

def team_defensive_capacity(team):
    team_players = team.players  
    player_stats = player_defensive_capacity(team_players)

    total_capacity = sum(player['defensive_capacity'] for player in player_stats if 'defensive_capacity' in player)
    total_players = sum(1 for player in player_stats if 'defensive_capacity' in player)  

    team_capacity = total_capacity / total_players if total_players > 0 else 0

    return team_capacity

