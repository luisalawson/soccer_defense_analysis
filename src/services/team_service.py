
import pandas as pd
from src.services.player_service import player_defensive_capacity
from src.utils.data_processing import load_data


def team_defensive_capacity(team):
    team_players = team.players  
    player_stats = player_defensive_capacity(team_players)

    total_capacity = sum(player['defensive_capacity'] for player in player_stats if 'defensive_capacity' in player)
    total_players = sum(1 for player in player_stats if 'defensive_capacity' in player)  

    team_capacity = total_capacity / total_players if total_players > 0 else 0

    return team_capacity

def team_ppda(team, df=load_data('src/data/matchData.csv')):
    # Definir los eventos defensivos relevantes
    defensive_events = ['Interception', 'Ball recovery', 'Shield ball opp', 'Challenge', 
                        'Foul', 'Tackle', 'Clearance', 'Aerial']
    
    team_id = team.team_id  # Obtenemos el ID del equipo
    
    # Filtrar los partidos donde juega el equipo actual (team_id)
    team_matches_ids = df[(df['team_id'] == team_id)]['match_id'].unique()

    # Filtrar el DataFrame completo solo por esos partidos (match_id)
    relevant_matches = df[df['match_id'].isin(team_matches_ids)]

    print(f"Partidos relevantes para el equipo {team_id}: {len(team_matches_ids)}")

    # Filtrar los pases permitidos por el equipo contrario (x < 60)
    opponent_passes = relevant_matches[(relevant_matches['team_id'] != team_id) & (relevant_matches['description'] == 'Pass') & (df['x'] < 60)]

    # Filtrar todas las acciones defensivas del equipo propio (x > 40)
    defensive_actions = relevant_matches[(relevant_matches['team_id'] == team_id) & (relevant_matches['description'].isin(defensive_events)) & (df['x'] > 40)]

    # Calcular el número de pases permitidos y el número de acciones defensivas
    num_opponent_passes = opponent_passes.shape[0]
    num_defensive_actions = defensive_actions.shape[0]

    # Revisión para evitar divisiones incorrectas
    if num_defensive_actions == 0:
        print(f"No se encontraron acciones defensivas para el equipo {team.team_id}")
        return float('inf')
    
    # Calcular el PPDA (Pases permitidos por cada acción defensiva)
    ppda = num_opponent_passes / num_defensive_actions

    # Imprimir los valores para revisar
    print(f"Equipo {team.team_id} | Pases permitidos: {num_opponent_passes} | Acciones defensivas: {num_defensive_actions} | PPDA: {ppda}")

    return ppda
