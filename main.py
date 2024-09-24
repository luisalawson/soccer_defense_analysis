from tqdm import tqdm
from src.utils.data_processing import load_data
from src.services.season_service import process_season_data
from src.services.team_service import team_defensive_capacity, team_ppda
import pandas as pd

def main():
    df = load_data('src/data/matchData.csv')
    
    # Procesar la temporada y obtener los equipos
    seasons, matches, all_teams = process_season_data(df)  

    print(f"Processed {len(seasons)} seasons.")

    # Crear un DataFrame para los jugadores
    columns_players = [
        "team_id", "team_name", "player_name", "position", "team_name_player", 
        "defensive_capacity_player", "successful_interception", "successful_tackle", 
        "successful_clearance", "successful_aerial", "total_events"
    ]
    
    df_output_players = pd.DataFrame(columns=columns_players)

    for team_id, team in all_teams.items():
        for player in team.players:
            player_data = {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "player_name": player.player_name,
                "position": player.position,
                "team_name_player": player.player_team,
                "defensive_capacity_player": player.metrics.get('defensive_capacity', 'N/A'),
                "successful_interception": player.metrics.get('successful_interception', 0),
                "successful_tackle": player.metrics.get('successful_tackle', 0),
                "successful_clearance": player.metrics.get('successful_clearance', 0),
                "successful_aerial": player.metrics.get('successful_aerial', 0),
                "total_events": (
                    player.metrics.get('total_interception', 0) + 
                    player.metrics.get('total_tackle', 0) + 
                    player.metrics.get('total_clearance', 0) + 
                    player.metrics.get('total_aerial', 0)
                )
            }
            
            df_output_players = df_output_players.append(player_data, ignore_index=True)

    # Guardar los datos de los jugadores en un CSV
    df_output_players.to_csv('/Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/players_data.csv', index=False)
    print("Datos de jugadores guardados en /Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/players_data.csv")

    # Crear un DataFrame para los equipos
    columns_teams = ["team_id", "team_name", "team_ppda", "team_defensive_capacity"]
    df_output_teams = pd.DataFrame(columns=columns_teams)

    # Calcular PPDA y capacidad defensiva para cada equipo
    for team_id, team in all_teams.items():
        ppda_value = team_ppda(team, df)  # Calcula el PPDA
        defensive_capacity_value = team_defensive_capacity(team)  # Calcula la capacidad defensiva

        team_data = {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "team_ppda": ppda_value,
            "team_defensive_capacity": defensive_capacity_value
        }

        df_output_teams = df_output_teams.append(team_data, ignore_index=True)

    # Guardar los datos de los equipos en un CSV
    df_output_teams.to_csv('/Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/teams_data.csv', index=False)
    print("Datos de equipos guardados en /Users/pgule/Documents/TD8/soccer_defense_analysis-main/src/data/teams_data.csv")

    # Mostrar el ranking de las temporadas
    for season in seasons.values():
        print(f"Season Ranking: {season.build_ranking()}")

if __name__ == '__main__':
    main()
