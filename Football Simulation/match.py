import random
import logging

from scipy.stats import poisson

logging.basicConfig(filename='log.txt', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# TODO: Add docstrings

class Match:
    def __init__(self, HomeTeam, AwayTeam, league_averages):
        self.home = HomeTeam
        self.away = AwayTeam
        self.max_goals = 5
        self.averages = league_averages
    
    def expected_score(self):
        exp_hgs = self.home.h_att*self.away.a_def*self.averages['HGS']
        exp_ags = self.away.a_att*self.home.h_def*self.averages['AGS']
        return exp_hgs, exp_ags
    
    def score_probabilities(self, exp_hgs, exp_ags):
        hm_g_probs = [poisson.pmf(goal, exp_hgs) for goal
                    in list(range(self.max_goals))]
        aw_g_probs = [poisson.pmf(goal, exp_ags) for goal
                    in list(range(self.max_goals))]
        return hm_g_probs, aw_g_probs
    
    def simulate_score(self, hm_g_probs, aw_g_probs):
        self.home_goals = int(random.choices(list(range(self.max_goals)),
                                         weights=hm_g_probs, k=1)[0])
        self.away_goals = int(random.choices(list(range(self.max_goals)),
                                         weights=aw_g_probs, k=1)[0])
        
    def allocate_points(self):
        if self.home_goals > self.away_goals:
            self.home.points +=3
        elif self.away_goals > self.home_goals:
            self.away.points +=3
        elif self.home_goals == self.away_goals:
            self.home.points +=1
            self.away.points +=1
    
    def allocate_goals(self):
        self.home.goals_scored += self.home_goals
        self.home.goals_allowed += self.away_goals
        
        self.away.goals_scored += self.away_goals
        self.away.goals_allowed += self.home_goals
        
    def simulate_match(self):
        logging.info('Simulation started')
        expected_goals = self.expected_score()
        goal_probs = self.score_probabilities(*expected_goals)
        self.simulate_score(*goal_probs)
        self.allocate_goals()
        self.allocate_points()
        logging.info('Simulation completed successfully')