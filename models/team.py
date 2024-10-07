from src.services.team_service import team_defensive_capacity, get_zone, team_ppda
from src.utils.data_processing import load_data
import numpy as np


class Team:
    def __init__(self, team_id, name, players, results_home, results_away):
        self.team_id = team_id
        self.team_name = name
        self.players = players
        self.results_home = results_home
        self.results_away = results_away
        # self.ppda = team_ppda(self, df=load_data('src/data/matchData.csv'))
        self.matches = []
        self.shot_matrix = None
        self.goal_matrix = None
        self.pass_matrix = None
        self.errors_matrix = None
        self.pass_transitions = None
        # self.defensive_capacity = team_defensive_capacity(self)
       
    def add_match(self, match):
        self.matches.append(match)

    def calculate_matrices(self):
        self.shot_matrix = self.build_shot_matrix()
        self.goal_matrix = self.build_goal_matrix()
        self.pass_matrix = self.build_pass_matrix()
        self.errors_matrix = self.build_errors_matrix()
        self.pass_transitions = self.build_pass_direction_matrix()

    def wins(self):
        wins = 0
        for result in self.results_home:
            if result[0] >result[1]:
                wins+=1
        for result in self.results_away:
            if result[0] >result[1]:
                wins+=1
        return wins
    
    def draws(self):
        draw = 0
        for result in self.results_home:
            if result[0]  == result[1]:
                draw+=1
        for result in self.results_away:
            if result[0]  == result[1]:
                draw+=1
        return draw
    
    def losses(self):
        loss = 0
        for result in self.results_home:
            if result[0]  < result[1]:
                loss+=1
        for result in self.results_away:
            if result[0]  < result[1]:
                loss+=1
        return loss
    
    def get_points(self):
        return (3*self.wins() + 1*self.draws() )
    
    def build_shot_matrix(self, player=None):
        shot_matrix = np.zeros((10, 10)) 
        shot_events = ['Miss', 'Post', 'Attempt Saved', 'Goal']  
        minutes_played = 0
        for match in self.matches:
            if player!= None:
                match_no_player = match.df[match.df['playerName']!= player.player_name]
                match_df = match_no_player.reset_index(drop=True)
            else:
                match_df = match.df.reset_index(drop=True)
            match_duration = match.duration / 60 
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    if event_type in shot_events: 
                        
                        x = round(float(row['x'].replace(',', '.')))  
                        y = round(float(row['y'].replace(',', '.'))) 
                        # print(f"x: {x}, y: {y}, type(x): {type(x)}, type(y): {type(y)}")
                        if 0 <= x < 100 and 0 <= y < 100:
                            zone_x, zone_y = get_zone(x, y) 
                            shot_matrix[zone_x, zone_y] += 1 
            minutes_played += match_duration
        shot_matrix /= minutes_played
        return shot_matrix
    
    def build_goal_matrix(self, player=None):
        goal_matrix = np.zeros((10, 10)) 
        minutes_played = 0
        for match in self.matches:
            if player!= None:
                match_no_player = match.df[match.df['playerName']!= player.player_name]
                match_df = match_no_player.reset_index(drop=True)
            else:
                match_df = match.df.reset_index(drop=True)
            match_duration = match.duration / 60
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    if event_type == 'Goal':
                        x = round(float(row['x'].replace(',', '.')))
                        y = round(float(row['y'].replace(',', '.')))
                        if 0 <= x < 100 and 0 <= y < 100:
                            zone_x, zone_y = get_zone(x, y) 
                            goal_matrix[zone_x, zone_y] += 1  
            minutes_played += match_duration
        goal_matrix /= minutes_played
        return goal_matrix
    
    def build_pass_matrix(self, player=None):
        pass_matrix = np.zeros((10, 10))  
        minutes_played = 0
        for match in self.matches:
            if player!= None:
                match_no_player = match.df[match.df['playerName']!= player.player_name]
                match_df = match_no_player.reset_index(drop=True)
            else:
                match_df = match.df.reset_index(drop=True)
            match_duration = (match.duration) / 60
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    outcome = row['outcome']
                    if event_type == 'Pass' and outcome == 1:
                        x = round(float(row['x'].replace(',', '.')))
                        y = round(float(row['y'].replace(',', '.')))
                        if 0 <= x < 100 and 0 <= y < 100:
                            zone_x, zone_y = get_zone(x, y) 
                            pass_matrix[zone_x, zone_y] += 1 
            minutes_played += match_duration
        pass_matrix /= minutes_played
        return pass_matrix

    def build_defense_matrix(self, player=None):
        defense_matrix = np.zeros((10, 10)) 
        minutes_played = 0
        defensive_events = ['Interception', 'Save', 'Ball recovery', 'Offside provoked', 'Shield ball opp', 'Tackle', 'Clearance', 'Aerial']
        for match in self.matches:
            if player!= None:
                match_no_player = match.df[match.df['playerName']!= player.player_name]
                match_df = match_no_player.reset_index(drop=True)
            else:
                match_df = match.df.reset_index(drop=True)
            match_duration = (match.duration) / 60
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    outcome = row['outcome']
                    if event_type in defensive_events and outcome == 1:
                        x = round(float(row['x'].replace(',', '.')))
                        y = round(float(row['y'].replace(',', '.')))
                        if 0 <= x < 100 and 0 <= y < 100:
                            zone_x, zone_y = get_zone(x, y) 
                            defense_matrix[zone_x, zone_y] += 1 
            minutes_played += match_duration
        defense_matrix /= minutes_played
        return defense_matrix

    def build_errors_matrix(self, player=None):
        errors_matrix = np.zeros((10, 10)) 
        minutes_played = 0
        errors_events = ['Challenge', 'Foul', 'Tackle', 'Clearance', 'Aerial']
        
        for match in self.matches:
            if player!= None:
                match_no_player = match.df[match.df['playerName']!= player.player_name]
                match_df = match_no_player.reset_index(drop=True)
            else:
                match_df = match.df.reset_index(drop=True)
            match_duration = (match.duration) / 60
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    outcome = row['outcome']
                    if (event_type in errors_events and outcome == 0) or (event_type == 'Error' and outcome == 1):
                        x = round(float(row['x'].replace(',', '.')))
                        y = round(float(row['y'].replace(',', '.')))
                        if 0 <= x < 100 and 0 <= y < 100:
                            zone_x, zone_y = get_zone(x, y) 
                            errors_matrix[zone_x, zone_y] += 1  
            minutes_played += match_duration
        errors_matrix /= minutes_played
        return errors_matrix

    def build_pass_direction_matrix(self):
        num_zones = 10  
        pass_direction_matrix = np.zeros((num_zones, num_zones, num_zones, num_zones)) 

        for match in self.matches:
            match_df = match.df.reset_index(drop=True)
            for i, row in match_df.iterrows():
                team = row['team_id']
                if team == self.team_id:
                    event_type = row['description']
                    outcome = row['outcome']
                    if event_type == 'Pass' and outcome == 1:
                        x_start = round(float(row['x'].replace(',', '.')))
                        y_start = round(float(row['y'].replace(',', '.')))
                        if i + 1 < len(match_df):
                            next_row = match_df.iloc[i + 1]
                            x_end = round(float(next_row['x'].replace(',', '.')))
                            y_end = round(float(next_row['y'].replace(',', '.')))
                        else:
                            continue
                        
                        # Obtener las zonas de inicio y fin
                        start_zone_x, start_zone_y = get_zone(x_start, y_start, num_zones)
                        end_zone_x, end_zone_y = get_zone(x_end, y_end, num_zones)

                        # Incrementar el contador de la matriz
                        pass_direction_matrix[start_zone_x, start_zone_y, end_zone_x, end_zone_y] += 1

        # Normalizar la matriz para que las filas sumen 1
        for zone_x_start in range(num_zones):
            for zone_y_start in range(num_zones):
                total_passes_from_zone = np.sum(pass_direction_matrix[zone_x_start, zone_y_start])
                if total_passes_from_zone > 0:
                    # Normalizar solo si hay pases desde la zona de inicio
                    pass_direction_matrix[zone_x_start, zone_y_start] /= total_passes_from_zone
                else:
                    # Imprimir advertencia si no hay pases desde esta zona
                    print(f"Advertencia: No hay pases desde la zona ({zone_x_start}, {zone_y_start}).")

        return pass_direction_matrix


    



    

    



    

        

