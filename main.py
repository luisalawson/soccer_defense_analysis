from tqdm import tqdm
from src.utils.data_processing import load_data
from src.services.season_service import process_season_data
from src.services.match_service import match_outcome, group_plays
import pandas as pd

def main():
    df = load_data('src/data/matchData.csv')
    
    seasons, matches, all_teams = process_season_data(df)  

    print(f"Processed {len(seasons)} seasons.")

    columns = [
        "team_id", "team_name", "player_name", "position", "team_name_player", 
        "defensive_capacity_player", "successful_interception", "successful_tackle", 
        "successful_clearance", "successful_aerial", "total_events"
    ]
    
    df_output = pd.DataFrame(columns=columns)

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
            
            df_output = df_output.append(player_data, ignore_index=True)

    df_output.to_csv('/Users/luisalawson/Desktop/SoccerDefenseAnalysis/src/data/players_data.csv', index=False)
    print("Datos guardados en /Users/luisalawson/Desktop/SoccerDefenseAnalysis/src/data/players_data.csv")

    for season in seasons.values():
        print(f"Season Ranking: {season.build_ranking()}")

if __name__ == '__main__':
    main()
