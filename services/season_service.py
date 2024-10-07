from src.models.season import Season
from datetime import datetime
from src.models.match import Match
from src.models.player import Player
from src.models.team import Team
from src.services.match_service import match_outcome, group_plays
from tqdm import tqdm



def team_name_id_pair(df, team_id):
    '''
    dado un id, devuelve el nombre
    '''
    try:
        row = df.loc[df['home_team_id'] == team_id].iloc[0]
        return row['home_team_name']  
    except IndexError:
        return None  

def get_match_duration(match_df, match_id):
    '''
    dtype: int
    rtype: tupla (int,int) 
    '''
    try:
        first_half_start = match_df.loc[(match_df['description'] == 'Start') & (match_df['period_id'] == 1), 'time'].iloc[0]
        first_half_end = match_df.loc[(match_df['description'] == 'End') & (match_df['period_id'] == 1), 'time'].iloc[0]
        second_half_start = match_df.loc[(match_df['description'] == 'Start') & (match_df['period_id'] == 2), 'time'].iloc[0]
        second_half_end = match_df.loc[(match_df['description'] == 'End') & (match_df['period_id'] == 2), 'time'].iloc[0]

        match_date = match_df['date'].iloc[0]
        first_half_start_time = datetime.strptime(f"{match_date} {first_half_start}", "%d%b%Y %I:%M:%S %p")
        first_half_end_time = datetime.strptime(f"{match_date} {first_half_end}", "%d%b%Y %I:%M:%S %p")
        second_half_start_time = datetime.strptime(f"{match_date} {second_half_start}", "%d%b%Y %I:%M:%S %p")
        second_half_end_time = datetime.strptime(f"{match_date} {second_half_end}", "%d%b%Y %I:%M:%S %p")

        first_half_duration = (first_half_end_time - first_half_start_time).seconds
        second_half_duration = (second_half_end_time - second_half_start_time).seconds

        return match_date, first_half_duration, second_half_duration
        
    except IndexError:
        return None

def get_players(df, team_id):
    '''
    Dado un df de equipo, devuelve todos los jugadores, excluyendo a los sustitutos. 
    Se asigna la posición más ofensiva cuando un jugador ha jugado en varias posiciones.
    '''
    position_priority = {
        'striker': 1,
        'midfielder': 2,
        'defender': 3,
        'goalkeeper': 4,
        'substitute': 5
    }
    my_players = df[df['team_id']==team_id]
    player_match_counts = my_players.groupby('playerName')['match_id'].nunique().reset_index()
    player_match_counts.columns = ['playerName', 'matches_played']
    
    positions = my_players[['playerName', 'playerPosition']].drop_duplicates()
    positions['position_priority'] = positions['playerPosition'].str.lower().map(position_priority)

    best_position = positions.loc[positions.groupby('playerName')['position_priority'].idxmin()].reset_index(drop=True)
    
    player_match_counts = player_match_counts.merge(best_position[['playerName', 'playerPosition']], on='playerName', how='left')
    
    all_players = player_match_counts.sort_values(by='matches_played', ascending=False)

    return all_players


def process_season_data(df):
    seasons = {}
    matches = []
    unique_seasons = df['season_id'].unique()
    all_teams = {}

    for season_id in tqdm(unique_seasons, desc="Processing Seasons", unit="season"):
        season_df = df[df['season_id'] == season_id]
        unique_matches = season_df['match_id'].unique()
        unique_teams = season_df['home_team_id'].unique()

        team_name_id_list = []
        for team_id in tqdm(unique_teams, desc="Processing Team", unit="team"):
            team_name = team_name_id_pair(season_df, team_id)
            if team_name:
                team_name_id_list.append((team_name, team_id))

                players_df = season_df[season_df['home_team_id'] == team_id]
                players_data = get_players(players_df, team_id)
                player_names = players_data['playerName'].tolist()
                player_positions = players_data['playerPosition'].tolist()

                season_instance = Season(season_id, season_df, [], team_name_id_list)

                players = [Player(season_instance, name, team_name, position) for name, position in zip(player_names, player_positions)]

                if team_id not in all_teams:
                    all_teams[team_id] = Team(team_id, team_name, [], [], [])

                all_teams[team_id].players.extend(players)

        season_matches = []

        for match_id in tqdm(unique_matches, desc="Processing Match", unit="match"):
            match_df = season_df[season_df['match_id'] == match_id]

            home_team_id = match_df['home_team_id'].iloc[0]
            away_team_id = match_df['away_team_id'].iloc[0]

            home_team = all_teams.get(home_team_id)
            away_team = all_teams.get(away_team_id)

            duration_data = get_match_duration(match_df, match_id)

            if duration_data:
                date = duration_data[0]
                first_half_duration = duration_data[1]
                second_half_duration = duration_data[2]
                total_duration = first_half_duration + second_half_duration

                match_instance = Match(match_id, date, total_duration, home_team, away_team, home_team_id, away_team_id, match_df)
                matches.append(match_instance)
                season_matches.append(match_instance)

                result_home = (match_instance.home_goals, match_instance.away_goals)
                result_away = (match_instance.away_goals, match_instance.home_goals)
                home_team.results_home.append(result_home)
                away_team.results_away.append(result_away)

                home_team.add_match(match_instance)  
                away_team.add_match(match_instance)  

        # for team in all_teams.values():
        #     team.calculate_matrices()

        season_instance.matches = season_matches
        if season_id not in seasons:
            seasons[season_id] = season_instance

    return seasons, matches, all_teams







