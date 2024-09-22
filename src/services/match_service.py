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
        
        # Si es un gol válido
        if description == 'Goal' and outcome == 1:
            next_pass_team_id = None

            # Buscar el siguiente evento que sea un pase
            for j in range(i + 1, len(match_df)):
                next_event = match_df.iloc[j]
                if next_event['description'] == 'Pass':
                    next_pass_team_id = next_event['team_id']
                    break  # Encontramos el siguiente pase, salimos del bucle

            # Si encontramos el próximo pase
            if next_pass_team_id is not None:
                # Si el pase es del mismo equipo que anotó, es un autogol
                if team_id == home_team_id and next_pass_team_id == home_team_id:
                    away_score += 1  # Autogol del equipo local, cuenta para el equipo visitante
                elif team_id == away_team_id and next_pass_team_id == away_team_id:
                    home_score += 1  # Autogol del equipo visitante, cuenta para el equipo local
                else:
                    # Gol normal
                    if team_id == home_team_id:
                        home_score += 1
                    else:
                        away_score += 1
            else:
                # No encontramos un pase, asumimos que es un gol normal
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
    df_copy = df.copy()
    df_copy['dangerous_zone'] = df_copy['x'].apply(
        lambda value: 1 if 0 <= float(value.replace(',', '.')) <= 30 else 0
    )
    
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


# def team_defensive_capacity(df, team_name, match):
#     team_players = df[(df['team_id'] == team_name) & (df['match_id'] == match)]['playerName'].unique()
    
#     player_stats = player_defensive_capacity(df, team_players, match)
    
#     total_capacity = sum(player['defensive_capacity'] for player in player_stats if 'defensive_capacity' in player)
#     total_players = len(player_stats)
    
#     team_capacity = total_capacity / total_players if total_players > 0 else 0
    
#     return {
#         'team_name': team_name,
#         'match_id': match,
#         'average_defensive_capacity': team_capacity,
#         'player_stats': player_stats,
#     }

# def player_defensive_capacity(df, player_names, match):
#     defensive_events = {
#         'Interception': {'successful': 1},
#         'Save': {'successful': 1},
#         'Ball recovery': {'successful': 1},
#         'Error': {'unsuccessful': 1},
#         'Offside provoked': {'successful': 1},
#         'Shield ball opp': {'successful': 1},
#         'Challenge': {'unsuccessful': 0},
#         'Foul': {'unsuccessful': 0},  
#         'Tackle': {'successful': 1, 'unsuccessful': 0},
#         'Clearance': {'successful': 1, 'unsuccessful': 0},
#         'Aerial': {'successful': 1, 'unsuccessful': 0},
#     }

#     player_stats = []

#     for player_name in player_names:
#         if player_name in ['nan', 'NaN']:
#             continue

#         player_df = df[df['playerName'] == player_name]

#         if not player_df.empty:
#             team_id = player_df['team_id'].iloc[0] if not player_df['team_id'].empty else None
#             position = next((pos for pos in player_df['playerPosition'] if pos.lower() != 'substitute'), None)

#             stats = {
#                 'player_name': player_name,
#                 'team_id': team_id,
#                 'position': position,
#             }

#             total_defensive_events = 0
#             successful_defensive_events = 0

#             for event, outcomes in defensive_events.items():
#                 if event == 'Foul':
#                     total_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == 0)].shape[0]
#                 else:
#                     total_event_count = player_df[player_df['description'] == event].shape[0]

#                 stats[f'total_{event.lower().replace(" ", "_")}'] = total_event_count
#                 total_defensive_events += total_event_count

#                 if 'successful' in outcomes:
#                     if event == 'Foul':
#                         successful_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == 0)].shape[0]
#                     else:
#                         successful_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == outcomes['successful'])].shape[0]

#                     stats[f'successful_{event.lower().replace(" ", "_")}'] = successful_event_count
#                     successful_defensive_events += successful_event_count

#                 for outcome_name, outcome_value in outcomes.items():
#                     if outcome_name != 'successful':
#                         if event == 'Foul' and outcome_value == 1:
#                             continue  
#                         outcome_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == outcome_value)].shape[0]
#                         stats[f'{outcome_name}_{event.lower().replace(" ", "_")}'] = outcome_event_count

#             stats['defensive_capacity'] = successful_defensive_events / total_defensive_events if total_defensive_events > 0 else 0
#             player_stats.append(stats)

#     return player_stats
