
from src.services.player_service import player_defensive_capacity, player_time, player_passes
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import StandardScaler
from src.utils.data_processing import load_data


class Player:
    def __init__(self, season, name, team, position):
        self.season = season
        self.player_name = name
        self.player_team = team
        self.position = position
        # self.metrics = self.calculate_metrics()
        # self.time_played = player_time(self)

    def calculate_metrics(self):
        player_stats = player_defensive_capacity([self.player_name])
        passes = player_passes(self)
        metrics = {}
        if player_stats:
            metrics.update(player_stats[0])  
        metrics.update(passes)
        return metrics


    def __repr__(self):
        return f"Player(name={self.player_name}, team={self.player_team}, metrics={self.metrics})"
    

       