
from src.services.player_service import player_defensive_capacity

class Player:
    def __init__(self, name, team, position):
        self.player_name = name
        self.player_team = team
        self.position = position
        self.metrics = self.calculate_metrics()

    def calculate_metrics(self):
        player_stats = player_defensive_capacity([self.player_name])
        
        if player_stats:
            return player_stats[0]  
        else:
            return {}  

    def __repr__(self):
        return f"Player(name={self.player_name}, team={self.player_team}, metrics={self.metrics})"

       