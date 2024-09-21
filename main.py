from tqdm import tqdm
from src.utils.data_processing import load_data
from src.services.season_service import process_season_data
from src.services.match_service import match_outcome, group_plays

def main():
    df = load_data('src/data/matchData.csv')
    seasons, matches = process_season_data(df)

    print(f"Processed {len(seasons)} seasons.")

    if matches:
        for match in matches:
            print(f"Testing Match ID: {match.match_id}, Date: {match.date}")
            print(f"Home Goals: {match.home_goals}, Away Goals: {match.away_goals}")
            print(f"Home Plays: {match.home_plays}, Away Plays: {match.away_plays}")
            print(f"Home Passes: {match.home_passes}, Away Passes: {match.away_passes}")
            print("-" * 40)
    else:
        print("No matches found.")

if __name__ == '__main__':
    main()



