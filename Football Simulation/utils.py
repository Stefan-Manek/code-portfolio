import http.client
import json
import urllib
from pathlib import Path
import logging
import time

import pandas as pd
import numpy as np

logging.basicConfig(filename='log.txt', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# TODO: Move these to main.py
API_KEY = '______'
API_PREFIX = 'api.football-data.org'

# TODO: Add docstrings

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def sort_dict(_dict):
    return dict(sorted(_dict.items(), key=lambda x:np.mean(x[1]), reverse=True))

def fetch_league_teams(league_name, league_ids, season='2021'):
    try:
        url = f'/v4/competitions/{league_ids[league_name]}/teams?'
        params = {'season' : season}
        url += urllib.parse.urlencode(params)
        connection = http.client.HTTPConnection(API_PREFIX)
        headers = { 'X-Auth-Token': API_KEY}
        connection.request('GET', url, None, headers )
        response = json.loads(connection.getresponse().read().decode())
        print(f'Requesting: {url}')
        logging.info('Requesting {league_name} teams at:\n{url}')
        return response
    
    except KeyError:
        logging.exception('League name not supported')
        print(('Unsupported League name entered. Full list of league '
            'IDs can be found at:\n'
            'https://docs.football-data.org/general/v4/lookup_tables.html'))
        
def team_info(league_name):
    teams_dict = fetch_league_teams(league_name)['teams']
    team_ids   = {team['name']: team['id'] for team in teams_dict}
    save_team_info(league_name, team_ids)
    return team_ids

def save_team_info(league_name, team_ids):
    league_dir = Path('League Data')
    league_dir.mkdir(parents=True, exist_ok=True)
    league_filename = Path.joinpath(league_dir, f'{league_name}_ids.json')
    with open(league_filename, 'w') as outfile:
        json.dump(team_ids, outfile)

def load_team_info(league_name):
    with open(f'League Data/{league_name}_ids.json') as f:
        data = json.load(f)
    return data
    

def get_matches_dict(team_id, season='2021'):
    try:
        url = f'/v2/teams/{team_id}/matches?'
        params = {'season' : season}
        url += urllib.parse.urlencode(params)
        connection = http.client.HTTPConnection(API_PREFIX)
        headers = { 'X-Auth-Token': API_KEY}
        connection.request('GET', url, None, headers)
        response = json.loads(connection.getresponse().read().decode())
        print('Requesting: {url}')
        logging.info('Requesting team matches at:\n{url}')
        return response
    
    except KeyError:
        logging.exception('Team Id incorrect')
        print(('Unsupported team ID entered. More info can be found at: '
            'https://docs.football-data.org/general/v4/lookup_tables.html'))


def get_goal_stats(match_dict, team_id, league_name='Premier League'):
    team_data = {
        'HGS': 0,
        'HGC': 0,
        'AGS': 0,
        'AGC': 0,
        'M_no': 0
        }
    for match in match_dict['matches']:
        if match['competition']['name'] == league_name:
            team_data['M_no'] += 1
            if match['homeTeam']['id'] == team_id:
                team_data['HGS'] += match['score']['fullTime']['homeTeam']
                team_data['HGC'] += match['score']['fullTime']['awayTeam']
            elif match['awayTeam']['id'] == team_id:
                team_data['AGS'] += match['score']['fullTime']['awayTeam']
                team_data['AGC'] += match['score']['fullTime']['homeTeam']
    return team_data


def league_goal_data(team_ids, league_name):
    league_data = {}
    for team, _id in team_ids.items():
        matches_dict = get_matches_dict(_id)
        league_data[team] = get_goal_stats(matches_dict, _id)
        time.sleep(6) #Limit of 10 requests/min
    league_df = build_league_df(league_data)
    save_league_data(league_df, league_name)
    return league_df

def build_league_df(league_data):
    data = {team : team_data.values() for team, team_data in
     league_data.items()}
    col_names = ['HGS', 'HGC', 'AGS', 'AGC', 'M_no']
    return pd.DataFrame.from_dict(data, orient='index', columns=col_names)

def save_league_data(league_df, league_name):
    league_dir = Path('League Data')
    league_dir.mkdir(parents=True, exist_ok=True)
    league_filename = Path.joinpath(league_dir, '%s.csv' % (league_name))
    league_df.to_csv(league_filename)
    
def read_league_data(league_name):
    league_df = pd.read_csv(f'League Data/{league_name}.csv', index_col=0)
    return league_df

def average_stats(league_df):
    tot_matches = sum(league_df['M_no'])/2 #Each team plays each other
    avg_stats = {
        'HGS': sum(league_df['HGS'])/(tot_matches),
        'AGS': sum(league_df['AGS'])/(tot_matches),
        'HGC': sum(league_df['HGC'])/(tot_matches),
        'AGC': sum(league_df['AGC'])/(tot_matches)
        }
    return avg_stats

def team_strengths(league_df, team_name):
    team_stats = league_df.loc[team_name]
    avg_stats = average_stats(league_df)
    label_map = {
        'HGS' : 'h_att',
        'AGS' : 'a_att',
        'HGC' : 'h_def',
        'AGC' : 'a_def'
    }
    team_strengths_dict = {label_map[category]: 
    team_stats[category]/19/avg_stats[category] for category in
     avg_stats.keys()}
    return team_strengths_dict