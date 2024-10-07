import pandas as pd

def match_outcome(df, home_team_id, away_team_id):
    '''
    Calcula el resultado de un partido dado un DataFrame.
    Tiene en cuenta goles y goles en contra, buscando el próximo pase después del gol.
    
    rtype: int, int (goles del equipo local, goles del equipo visitante)
    '''
    home_score = 0
    away_score = 0
    match_df = df.reset_index(drop=True)

    for i, row in match_df.iterrows():
        team_id = row['team_id']
        description = row['description']
        outcome = row['outcome']
        
        if description == 'Goal' and outcome == 1:
            next_pass_team_id = None

            for j in range(i + 1, len(match_df)):
                next_event = match_df.iloc[j]
                if next_event['description'] == 'Pass':
                    next_pass_team_id = next_event['team_id']
                    break  

            if next_pass_team_id is not None:
                if team_id == home_team_id and next_pass_team_id == home_team_id:
                    away_score += 1 
                elif team_id == away_team_id and next_pass_team_id == away_team_id:
                    home_score += 1  
                else:
                    if team_id == home_team_id:
                        home_score += 1
                    else:
                        away_score += 1

    return home_score, away_score


def categorize_dangerous(df):
    """
    Clasifica las jugadas como peligrosas según su posición en el campo.
    :rtype: pandas.DataFrame
    """
    #Luisa
    df_copy = df.copy()
    df_copy['dangerous_zone'] = df_copy['x'].apply(
        lambda value: 1 if 0 <= float(value.replace(',', '.')) <= 30 else 0
    )

    #Pato
    # df_copy = df.copy()
    # df_copy['dangerous_zone'] = df_copy['x'].apply(
    #     lambda value: 1 if 0 <= value <= 30 else 0
    # )
    
    return df_copy

def group_plays(match_df, skip_events, stop_events):
    
    home_plays = 0
    away_plays = 0
    home_passes = 0
    away_passes = 0
    home_dangerous_play = 0
    away_dangerous_play = 0

    modified_df = categorize_dangerous(match_df)
    match_df = modified_df.reset_index(drop=True)

    home_team_id = match_df['home_team_id'].iloc[0]
    away_team_id = match_df['away_team_id'].iloc[0]
    home_team_name = match_df['home_team_name'].iloc[0]
    away_team_name = match_df['away_team_name'].iloc[0]

    current_team = None
    in_play = False
    current_passes = 0
    play_in_danger_zone = []

    for i, row in match_df.iterrows():
        event = row['description']

        if event in skip_events:
            skip_condition = skip_events[event]
            if skip_condition is None or skip_condition == row['outcome']:
                continue

        if event in stop_events:
            play_end = row['time']
            stop_condition = stop_events[event]
            if stop_condition is None or stop_condition == row['outcome']:
                if in_play:
                    if current_team == home_team_id:
                        home_plays += 1
                        home_passes += current_passes
                        if sum(play_in_danger_zone) > 3:
                            home_dangerous_play += 1
                    elif current_team == away_team_id:
                        away_plays += 1
                        away_passes += current_passes
                        if sum(play_in_danger_zone) > 3:
                            away_dangerous_play += 1

                
                current_team = None
                in_play = False
                current_passes = 0
                play_in_danger_zone = []
                continue

        
        team_id = row['team_id']
        dangerous_area = row['dangerous_zone']
        play_in_danger_zone.append(dangerous_area)

        if current_team is None:
            current_team = team_id
            in_play = True
            current_passes = 0

        if current_team == team_id:
            if row['description'] == 'Pass' and row['outcome'] == 1:
                current_passes += 1
        else:
            
            if in_play:
                if current_team == home_team_id:
                    home_plays += 1
                    home_passes += current_passes
                    if sum(play_in_danger_zone) > 3:
                        home_dangerous_play += 1
                elif current_team == away_team_id:
                    away_plays += 1
                    away_passes += current_passes
                    if sum(play_in_danger_zone) > 3:
                        away_dangerous_play += 1

            
            current_team = team_id
            in_play = True
            current_passes = 0
            play_in_danger_zone = []

    return home_plays, away_plays, home_passes, away_passes

