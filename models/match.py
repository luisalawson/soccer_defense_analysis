from src.services.match_service import match_outcome, group_plays
import pandas as pd 

stop_events = {
    'Attempt saved': None,
    'Ball recovery': None,
    'Ball touch': None,
    'Take on': 0,  # Stops play only if outcome == 0
    'Clearance': 1,  # Stops play only if outcome == 1
    'Contentious referee decision': None,
    'Corner awarded': 0,  # Stops play only if outcome == 0
    'Dispossessed': None,
    'Error': None,
    'Foul': 0,  # Stops play only if outcome == 0
    'Goal': None,
    'Interception': None,
    'Keeper pick-up': None,
    'Keeper sweeper': None,
    'Miss': None,
    'Offside pass': None,
    'Out': 0,  # Stops play only if outcome == 0
    'Post': None,
    'Punch': None,
    'Smother': None,
    'Start delay': None,
    'End delay': None,
    'Tackle': None,
    'Pass': 0  # Stops play only if outcome == 0
}

skip_events = {
    'Chance missed':None, 
    'Collection End':None, 
    'Cross not claimed':None, 
    'Deleted event':None, 
    'Formation change':None, 
    'Good skill':None, 
    'Team set up':None, 
    'Start':None, 
    'Temp_Attempt':None,
    'Out':1,
    'Clearance':0,
    'Corner awarded': 1,
    'Aerial': 0,
    'Take on':1,
    # 'Foul': 1,
    'Claim':None,
    'Penalty faced':None,
    'Player on': None,
    'Player off': None,
    'Player retired': None,
    'Save':None,
    'Shield ball opp': None,
    'Card': None,
    'Challenge':None,
    'Foul throw-in':None,
    'Offside provoked':None
}

class Match:
    def __init__(self, match_id, date, duration, home_team, away_team,home_id, away_id, df):
        self.match_id = match_id
        self.date = date
        self.duration = duration
        self.home_team = home_team
        self.away_team = away_team
        self.home_id = home_id
        self.away_id = away_id
        self.df = df  
        self.home_goals, self.away_goals = match_outcome(df, home_id, away_id)
        self.home_plays, self.away_plays, self.home_passes, self.away_passes = group_plays(df,skip_events, stop_events)
        self.dc_local = 0
        self.dc_away = 0

    def winner(self):
        if self.home_goals > self.away_goals:
            return self.home_team
        elif self.home_goals < self.away_goals:
            return self.away_team
        else:
            return None
    
    def points(self):
        if self.winner() == self.home_team:
            return (3, 0)
        elif self.winner() == self.away_team:
            return (0, 3)
        else:
            return (1, 1)
    
    def total_plays(self):
        return self.home_plays + self.away_plays
    
    def total_passes(self):
        return self.home_passes + self.away_passes