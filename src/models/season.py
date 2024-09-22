
class Season:
    def __init__(self, season_id, df, matches, teams):
        self.season_id = season_id
        self.df = df
        self.matches = matches
        self.teams = teams
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
    
    def build_ranking(self):
        teams = {}
        for match in self.matches:
            home = match.home_team
            away = match.away_team
            match_points_home = match.points()[0]
            match_points_away = match.points()[1]
            goals_home = match.home_goals
            goals_away = match.away_goals

            if home not in teams:
                teams[home] = [match_points_home, goals_home, goals_home - goals_away]
            else:
                teams[home][0] += match_points_home
                teams[home][1] += goals_home
                teams[home][2] += goals_home - goals_away

            if away not in teams:
                teams[away] = [match_points_away, goals_away, goals_away - goals_home]
            else:
                teams[away][0] += match_points_away
                teams[away][1] += goals_away
                teams[away][2] += goals_away - goals_home

        sorted_teams = sorted(teams.items(), key=lambda x: (x[1][0], x[1][2]), reverse=True)

        return sorted_teams




        


        

    

   
