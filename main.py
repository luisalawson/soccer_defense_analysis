from tqdm import tqdm
from src.utils.data_processing import load_data
from src.services.season_service import process_season_data
from src.services.match_service import match_outcome, group_plays
import pandas as pd
import os


def main():
    df = load_data('src/data/matchData.csv')
    seasons, matches, all_teams = process_season_data(df)  
    print(f"Processed {len(seasons)} seasons.")
    
    for team_id, team in all_teams.items():
        if team.team_name  == 'Liverpool':
            print(f'Guardando matrices del equipo: {team.team_name}')
            save_team_matrices(team)
            
            evaluate_player_removal(team)

def save_team_matrices(team, player=None):
    """Guarda las matrices del equipo en una carpeta específica."""
    base_output_dir = '/Users/luisalawson/Desktop/SoccerDefenseAnalysis/src/data/'
    
    if player is None:
        output_dir = os.path.join(base_output_dir, team.team_name)
    else:
        output_dir = os.path.join(base_output_dir, team.team_name, f"sacando_a_{player.player_name}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    shot_matrix_df = pd.DataFrame(team.build_shot_matrix(player=player))
    shot_matrix_path = os.path.join(output_dir, "shot_matrix.csv")
    shot_matrix_df.to_csv(shot_matrix_path, index=False, header=False)
    print(f"Matriz de tiros lista {shot_matrix_path}")
    
    goal_matrix_df = pd.DataFrame(team.build_goal_matrix(player=player))
    goal_matrix_path = os.path.join(output_dir, "goal_matrix.csv")
    goal_matrix_df.to_csv(goal_matrix_path, index=False, header=False)
    print(f"Matriz de goles lista {goal_matrix_path}")

    pass_matrix_df = pd.DataFrame(team.build_pass_matrix(player=player))
    pass_matrix_path = os.path.join(output_dir, "pass_matrix.csv")
    pass_matrix_df.to_csv(pass_matrix_path, index=False, header=False)
    print(f"Matriz de pases lista {pass_matrix_path}")

    defense_matrix_df = pd.DataFrame(team.build_defense_matrix(player=player))
    defense_matrix_path = os.path.join(output_dir, "defense_matrix.csv")
    defense_matrix_df.to_csv(defense_matrix_path, index=False, header=False)
    print(f"Matriz de acciones defensivas lista {defense_matrix_path}")

    errors_matrix_df = pd.DataFrame(team.build_errors_matrix(player=player))
    errors_matrix_path = os.path.join(output_dir, "errors_matrix.csv")
    errors_matrix_df.to_csv(errors_matrix_path, index=False, header=False)
    print(f"Matriz de errores lista {errors_matrix_path}")

def evaluate_player_removal(team):
    """Genera y guarda matrices para cada jugador eliminado."""
    for player in team.players:
        player_name = player.player_name
        print(f"Guardando matrices del equipo sin el jugador: {player_name}")
        save_team_matrices(team, player=player)

if __name__ == '__main__':
    main()


# from tqdm import tqdm
# from src.utils.data_processing import load_data
# from src.services.season_service import process_season_data
# from src.services.team_service import team_defensive_capacity, team_ppda
# import pandas as pd

# def main():
#     df = load_data('src/data/matchData.csv')
    
#     # Procesar la temporada y obtener los equipos
#     seasons, matches, all_teams = process_season_data(df)  

#     print(f"Processed {len(seasons)} seasons.")

#     # Crear un DataFrame para los jugadores
#     columns_players = [
#         "team_id", "team_name", "player_name", "position", "team_name_player", 
#         "defensive_capacity_player", "successful_interception", "successful_tackle", 
#         "successful_clearance", "successful_aerial", "total_events"
#     ]
    
#     df_output_players = pd.DataFrame(columns=columns_players)

#     for team_id, team in all_teams.items():
#         for player in team.players:
#             player_data = {
#                 "team_id": team.team_id,
#                 "team_name": team.team_name,
#                 "player_name": player.player_name,
#                 "position": player.position,
#                 "team_name_player": player.player_team,
#                 "defensive_capacity_player": player.metrics.get('defensive_capacity', 'N/A'),
#                 "successful_interception": player.metrics.get('successful_interception', 0),
#                 "successful_tackle": player.metrics.get('successful_tackle', 0),
#                 "successful_clearance": player.metrics.get('successful_clearance', 0),
#                 "successful_aerial": player.metrics.get('successful_aerial', 0),
#                 "total_events": (
#                     player.metrics.get('total_interception', 0) + 
#                     player.metrics.get('total_tackle', 0) + 
#                     player.metrics.get('total_clearance', 0) + 
#                     player.metrics.get('total_aerial', 0)
#                 )
#             }
            
#             df_output_players = df_output_players.append(player_data, ignore_index=True)

#     # Guardar los datos de los jugadores en un CSV
#     df_output_players.to_csv('/Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/players_data.csv', index=False)
#     print("Datos de jugadores guardados en /Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/players_data.csv")

#     # Crear un DataFrame para los equipos
#     columns_teams = ["team_id", "team_name", "team_ppda", "team_defensive_capacity"]
#     df_output_teams = pd.DataFrame(columns=columns_teams)

#     # Calcular PPDA y capacidad defensiva para cada equipo
#     for team_id, team in all_teams.items():
#         ppda_value = team_ppda(team, df)  # Calcula el PPDA
#         defensive_capacity_value = team_defensive_capacity(team)  # Calcula la capacidad defensiva

#         team_data = {
#             "team_id": team.team_id,
#             "team_name": team.team_name,
#             "team_ppda": ppda_value,
#             "team_defensive_capacity": defensive_capacity_value
#         }

#         df_output_teams = df_output_teams.append(team_data, ignore_index=True)

#     # Guardar los datos de los equipos en un CSV
#     df_output_teams.to_csv('/Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/teams_data.csv', index=False)
#     print("Datos de equipos guardados en /Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/teams_data.csv")

#     # Mostrar el ranking de las temporadas
#     for season in seasons.values():
#         print(f"Season Ranking: {season.build_ranking()}")

# if __name__ == '__main__':
#     main()