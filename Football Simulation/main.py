import logging

import matplotlib.pyplot as plt
import seaborn as sb

from mpl_toolkits.axes_grid.inset_locator import inset_axes

import utils
from league import League

logging.basicConfig(filename='log.txt', level=logging.DEBUG)
logger = logging.getLogger(__name__)

LEAGUE_NAME = 'Premier League'

LEAGUE_IDS = utils.read_json('league_ids.json')
TEAM_PNGS = utils.read_json('club_crests.json')

def main(league_name, n=2):
    team_ids = utils.load_team_info(league_name)
    pts_dict = {team: [] for team in team_ids.keys()}
    for i in range(n):
        league = League(league_name, team_ids)
        league.simulate_league()
        for team in league.Teams:
            pts_dict[team.name].append(team.points)
    pts_dict = utils.sort_dict(pts_dict)

    fig, axs = plt.subplots(len(pts_dict), figsize=(18,16),
                            sharex=True, sharey=True)
    idx = 0
    for team, points in pts_dict.items(): #Very messy implementation
        sb.kdeplot(points, ax=axs[idx], bw_method=0.5, warn_singular=False)
        axs[idx].get_yaxis().set_visible(False)
        crest_im = plt.imread(TEAM_PNGS[team])
        inset_ax = inset_axes(axs[idx], height=0.4, width=0.4, loc=6) 
        inset_ax.imshow(crest_im)
        inset_ax.set_axis_off()
        idx+=1
        
    fig.text(0.5, 0.06, 'Points', ha='center', size='x-large')
    fig.text(0.5, 0.925, f'{league_name} points probabilities based on {n} simulations',
             ha='center', size='x-large', fontvariant='small-caps')
   
if __name__ == '__main__':
    main(LEAGUE_NAME)