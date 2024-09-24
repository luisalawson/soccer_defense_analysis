from src.utils.data_processing import load_data


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

