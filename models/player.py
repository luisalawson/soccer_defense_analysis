from src.services.player_service import player_defensive_capacity, player_time, player_passes
from src.services.team_service import get_zone
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import StandardScaler
from src.utils.data_processing import load_data
import numpy as np


class Player:
    def __init__(self, season, name, team, position):
        self.season = season
        self.player_name = name
        self.player_team = team
        self.position = position
        self.shot_matrix = np.zeros((10, 10))  
        self.goal_matrix = np.zeros((10, 10))  
        self.pass_matrix = np.zeros((10, 10)) 
        self.errors_matrix = np.zeros((10, 10)) 
        self.defense_matrix = np.zeros((10, 10))
        self.pass_direction_matrix_ = np.zeros((10, 10, 10, 10))
        self.time_played = player_time(self)
        self.cards = 0
        self.out_balls = np.zeros((10, 10))

    def calculate_metrics(self):
        player_stats = player_defensive_capacity([self.player_name])
        passes = player_passes(self)
        metrics = {}
        if player_stats:
            metrics.update(player_stats[0])  
        metrics.update(passes)
        return metrics
    
    def build_pass_direction_matrix(self, df=load_data('src/data/matchData.csv')):
        pass_direction_matrix = np.zeros((10, 10, 10, 10))
        matches = df[(df['home_team_name'] == self.player_team) | (df['away_team_name'] == self.player_team)]
        player_matches = matches[matches['playerName'] == self.player_name].reset_index(drop=True)
        for i, row in player_matches.iterrows():
            event_type = row['description']
            outcome = row['outcome']
            if event_type == 'Pass' and outcome == 1:
                x_start = round(float(row['x'].replace(',', '.')))
                y_start = round(float(row['y'].replace(',', '.')))
                if i + 1 < len(player_matches):
                    next_row = player_matches.iloc[i + 1]
                    x_end = round(float(next_row['x'].replace(',', '.')))
                    y_end = round(float(next_row['y'].replace(',', '.')))
                else:
                    continue
                start_zone_x, start_zone_y = get_zone(x_start, y_start, 10)
                end_zone_x, end_zone_y = get_zone(x_end, y_end, 10)
                pass_direction_matrix[start_zone_x, start_zone_y, end_zone_x, end_zone_y] += 1
                # print(f"Pase desde zona ({start_zone_x}, {start_zone_y}) a zona ({end_zone_x}, {end_zone_y})")
        for zone_x_start in range(10):
            for zone_y_start in range(10):
                total_passes_from_zone = np.sum(pass_direction_matrix[zone_x_start, zone_y_start])
                if total_passes_from_zone > 0:
                    pass_direction_matrix[zone_x_start, zone_y_start] /= total_passes_from_zone
                else:
                    print(f"Advertencia: No hay pases desde la zona ({zone_x_start}, {zone_y_start}).")
        self.pass_direction_matrix_ = pass_direction_matrix
    
    def update_player_matrices(self, df=load_data('src/data/matchData.csv')):
        """
        Actualiza las matrices individuales del jugador basado en los eventos del partido.
        """
        matches = df[(df['home_team_name'] == self.player_team) | (df['away_team_name'] == self.player_team)]
        if self.position != 'Goalkeeper':
            for i, row in matches.iterrows():
                if row['playerName'] == self.player_name:
                    event_type = row['description']
                    event_outcome = row['outcome']
                    x = round(float(row['x'].replace(',', '.')))
                    y = round(float(row['y'].replace(',', '.')))
                    if 0 <= x < 100 and 0 <= y < 100:
                        zone_x, zone_y = get_zone(x, y)
                        if event_type in ['Miss', 'Post', 'Attempt Saved', 'Goal']:
                            self.shot_matrix[zone_x, zone_y] += 1
                            if event_type == 'Goal':
                                self.goal_matrix[zone_x, zone_y] += 1
                        elif event_type == 'Pass' and event_outcome==1:
                            self.pass_matrix[zone_x, zone_y] += 1
                        elif event_type == 'Error' and event_outcome ==1:
                            self.errors_matrix[zone_x, zone_y] += 1
                        elif event_type in ['Interception', 'Save', 'Ball recovery', 'Offside provoked', 'Shield ball opp', 'Tackle', 'Clearance', 'Aerial'] and event_outcome==1:
                            self.defense_matrix[zone_x, zone_y] += 1
                        elif event_type in ['Challenge', 'Foul', 'Tackle', 'Clearance', 'Aerial', 'Ball touch'] and event_outcome ==0:
                            self.errors_matrix[zone_x, zone_y] += 1
                        elif event_type == 'Card':
                            self.cards +=1
                    else:
                        if event_type == 'Out' and event_outcome == 0:
                            previous_event = df.iloc[i-1]
                            if previous_event['description'] != 'Out':
                                x = round(float(previous_event['x'].replace(',', '.')))
                                y = round(float(previous_event['y'].replace(',', '.')))
                            else:
                                previous_event = df.iloc[i-2]
                                x = round(float(previous_event['x'].replace(',', '.')))
                                y = round(float(previous_event['y'].replace(',', '.')))
                            zone_x, zone_y = get_zone(x, y)
                            self.out_balls[zone_x,zone_y] += 1
            self.errors_matrix/=self.time_played
            self.defense_matrix/=self.time_played
            self.goal_matrix/=self.time_played
            self.shot_matrix/=self.time_played
            self.pass_matrix/=self.time_played
            self.out_balls/=self.time_played
            self.cards /=self.time_played
        
        else:
            pass


    def __repr__(self):
        return f"Player(name={self.player_name}, team={self.player_team}, metrics={self.metrics})"
    

       