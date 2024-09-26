from src.utils.data_processing import load_data
import math

def player_defensive_capacity(player_names , df=load_data('src/data/matchData.csv')):
    defensive_events = {
        'Interception': {'successful': 1},
        'Save': {'successful': 1},
        'Ball recovery': {'successful': 1},
        'Error': {'unsuccessful': 1},
        'Offside provoked': {'successful': 1},
        'Shield ball opp': {'successful': 1},
        'Challenge': {'unsuccessful': 0},
        'Foul': {'unsuccessful': 0},  
        'Tackle': {'successful': 1, 'unsuccessful': 0},
        'Clearance': {'successful': 1, 'unsuccessful': 0},
        'Aerial': {'successful': 1, 'unsuccessful': 0},
    }

    player_stats = []

    for player_name in player_names:
        if player_name in ['nan', 'NaN']:
            continue

        player_df = df[df['playerName'] == player_name]

        if not player_df.empty:
            team_id = player_df['team_id'].iloc[0] if not player_df['team_id'].empty else None
            position = next((pos for pos in player_df['playerPosition'] if pos.lower() != 'substitute'), None)

            stats = {
                'player_name': player_name,
                'team_id': team_id,
                'position': position,
            }

            total_defensive_events = 0
            successful_defensive_events = 0

            for event, outcomes in defensive_events.items():
                if event == 'Foul':
                    total_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == 0)].shape[0]
                else:
                    total_event_count = player_df[player_df['description'] == event].shape[0]

                stats[f'total_{event.lower().replace(" ", "_")}'] = total_event_count
                total_defensive_events += total_event_count

                if 'successful' in outcomes:
                    if event == 'Foul':
                        successful_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == 0)].shape[0]
                    else:
                        successful_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == outcomes['successful'])].shape[0]

                    stats[f'successful_{event.lower().replace(" ", "_")}'] = successful_event_count
                    successful_defensive_events += successful_event_count

                for outcome_name, outcome_value in outcomes.items():
                    if outcome_name != 'successful':
                        if event == 'Foul' and outcome_value == 1:
                            continue  
                        outcome_event_count = player_df[(player_df['description'] == event) & (player_df['outcome'] == outcome_value)].shape[0]
                        stats[f'{outcome_name}_{event.lower().replace(" ", "_")}'] = outcome_event_count

            stats['defensive_capacity'] = successful_defensive_events / total_defensive_events if total_defensive_events > 0 else 0

            for event, outcomes in defensive_events.items():
                if 'successful' in outcomes:
                    total_event_count = stats[f'total_{event.lower().replace(" ", "_")}']
                    successful_event_count = stats[f'successful_{event.lower().replace(" ", "_")}']
                    success_percentage = (successful_event_count / total_event_count) * 100 if total_event_count > 0 else 0
                    stats[f'successful_percentage_{event.lower().replace(" ", "_")}'] = success_percentage

            player_stats.append(stats)

    return player_stats

def player_time(player, df=load_data('src/data/matchData.csv')):
    player_name  =  player.player_name
    team = player.player_team

    matches = df[(df['home_team_name'] == team) | (df['away_team_name'] == team)]
    unique_matches = matches['match_id'].unique()

    total_time = 0

    for match in unique_matches:
        match_df = matches[matches['match_id'] == match]
        players = match_df['playerName'].unique()

        if player_name not in players:
            continue

        match_start = 0
        match_end = match_df['min'].max()
        player_start = match_start
        player_end = match_end
        for index, row in match_df.iterrows():
            if row['description'] == 'Player on' and row['playerName'] == player_name:
                player_start = row['min']
            elif row['description'] == 'Player off' and row['playerName'] == player_name:
                player_end = row['min']
        
        total_time += (player_end - player_start)

    return total_time


def player_passes(player, df=load_data('src/data/matchData.csv')):
    ''' 
    me da todos los pases que hizo
    ademas, me da la distancia de los pases
    la cantidad de pases largos (mas de 10 mts)
    la cantidad de pases cortos (menos de 10mts)
    '''
    name = player.player_name
    team = player.player_team

    matches = df[(df['home_team_name'] == team) | (df['away_team_name'] == team)]
    unique_matches = matches['match_id'].unique()

    total_successful_passes = 0
    total_unsuccessful_passes = 0
    total_long_passes = 0
    total_short_passes = 0

    for match in unique_matches:
        match_df = matches[matches['match_id'] == match]
        players = match_df['playerName'].unique()

        if name not in players:
            continue

        for index, row in match_df.iterrows():
            if row['playerName'] == name:
                if row['outcome'] == 1:
                    start_x = float((row['x']).replace(',', '.'))
                    if index + 1 < len(match_df):
                        end_x_str = match_df.iloc[index + 1]['x']
                        end_x = float(end_x_str.replace(',', '.'))
                        pass_distance = abs(start_x - end_x)
                        if pass_distance >= 7:
                            total_long_passes += 1
                        else:
                            total_short_passes += 1
                    total_successful_passes += 1
                else:
                    total_unsuccessful_passes += 1
    
    return {
        'total_successful_passes': total_successful_passes,
        'total_unsuccessful_passes': total_unsuccessful_passes,
        'total_long_passes': total_long_passes,
        'total_short_passes': total_short_passes
    }
    
