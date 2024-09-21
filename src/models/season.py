
class Season:
    def __init__(self, season_id, df, matches, teams):
        self.season_id = season_id
        self.df = df
        self.matches = matches
        self.teams = teams
        self.ranking = []
        self.top_scorer = None
        self.least_goals_conceded = None
        self.total_goals = 0
    
    def get_teams(self):
        return self.teams
    
    def get_season_id(self):
        return self.season_id
    
    def get_matches(self):
        return self.matches
    
    def total_teams(self):
        return len(self.teams)
    
    def total_matches(self):
        return len(self.matches)
    

   
