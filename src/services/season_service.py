from src.models.season import Season
from datetime import datetime
from src.models.match import Match
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


def process_season_data(df):
    '''
    Crea temporadas y partidos a partir de un DataFrame.
    Retorna un diccionario de temporadas y una lista de partidos.
    '''
    seasons = {}
    matches = []  
    unique_seasons = df['season_id'].unique()

    for season in tqdm(unique_seasons, desc="Processing Seasons", unit="season"):
        season_df = df[df['season_id'] == season]
        unique_matches = season_df['match_id'].unique()
        unique_teams = season_df['home_team_id'].unique()

        team_name_id_list = []
        for team_id in unique_teams:
            team_name = team_name_id_pair(season_df, team_id)
            if team_name:
                team_name_id_list.append((team_name, team_id))

        season_matches = []  

        for match_id in tqdm(unique_matches, desc="Processing Match", unit="match"):
            match_df = season_df[season_df['match_id'] == match_id]
            home_team = match_df['home_team_name'].iloc[0]
            home_team_id = next((team_id for name, team_id in team_name_id_list if name == home_team), None)
            away_team = match_df['away_team_name'].iloc[0]
            away_team_id = next((team_id for name, team_id in team_name_id_list if name == away_team), None)
            duration_data = get_match_duration(match_df, match_id)
            
            if duration_data: 
                date = duration_data[0]
                first_half_duration = duration_data[1]
                second_half_duration = duration_data[2]
                total_duration = first_half_duration + second_half_duration

                match_instance = Match(match_id, date, total_duration, home_team, away_team, home_team_id, away_team_id, match_df)
                matches.append(match_instance)
                season_matches.append(match_instance)  

        if season not in seasons:
            seasons[season] = Season(season, season_df, season_matches, team_name_id_list)

    return seasons, matches




