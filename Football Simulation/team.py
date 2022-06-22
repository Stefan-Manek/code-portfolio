class Team:
    def __init__(self, name, h_att, a_att, h_def, a_def):
        self.name = name
        self.h_att = h_att
        self.h_def = h_def
        self.a_att = a_att
        self.a_def = h_def
        
        self.goals_scored = 0
        self.goals_allowed = 0
        self.points = 0
        
    def goal_diff(self):
        return int(self.goals_scored - self.goals_allowed)
        
    def team_data(self):
        return [self.goals_scored, self.goals_allowed, 
                self.goal_diff(), self.points]