import logging

from itertools import combinations
import pandas as pd

import utils
from team import Team
from match import Match

LEAGUE_IDS = utils.read_json('league_ids.json')

# TODO: Add docstrings

class League:
    def __init__(self, league_name, team_ids=None):
        self.name = league_name
        
        if team_ids is None:
            try:
                self.team_ids = utils.load_team_info(league_name)
                logging.info('Loading {self.name} team IDs from file')
            except FileNotFoundError:
                self.team_ids = utils.team_info(league_name)
                logging.exception('Could not find {self.name} Team IDs file')

        else: self.team_ids = team_ids
        
        self.teams = list(self.team_ids.keys())
        
        try:
            self.read_league_data()
            
        except FileNotFoundError:
            self.fetch_league_data()
        
        self.averages = utils.average_stats(self.league_df)
        
        #Creating team objects:
        self.Teams = [Team(name, **utils.team_strengths(self.league_df, name))
            for name in self.teams]
        
        self.Matches = [Match(*team_pair, self.averages) for 
                    team_pair in self.pair_teams()]
        
    def pair_teams(self):
        pairs1 = list(combinations(self.Teams, 2)) 
        pairs2 = [pair[::-1] for pair in combinations(self.Teams, 2)]
        return pairs1 + pairs2
    
    def fetch_league_data(self):
        print('Full dataset not found. Fetching data...')
        self.league_df = utils.league_goal_data(self.team_ids, self.name)
        
    def read_league_data(self):
        league_df = utils.read_league_data(self.name)
        if len(league_df.index) != len(self.team_ids):
            self.fetch_league_data()
        else: self.league_df = league_df
        
    def simulate_league(self):
        for match in self.Matches:
            match.simulate_match()
            
    def build_league_table(self):
        data = {team.name : team.team_data() for team in self.Teams}
        col_names = ['GS', 'GC', 'GD', 'Pts']
        return pd.DataFrame.from_dict(data, 
                                orient='index', 
                                columns=col_names).sort_values(by=['Pts'],
                                                               ascending=False)