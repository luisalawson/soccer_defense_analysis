from src.services.team_service import team_defensive_capacity
from src.services.team_service import team_ppda
from src.utils.data_processing import load_data


class Team:
    def __init__(self, team_id, name, players, results_home, results_away):
        self.team_id = team_id
        self.team_name = name
        self.players = players
        self.results_home = results_home
        self.results_away = results_away
        self.defensive_capacity = team_defensive_capacity(self)
        self.ppda = team_ppda(self, df=load_data('src/data/matchData.csv'))

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
    

        

