import re

import pandas as pd
import numpy as np

from urllib.request import urlopen
from bs4 import BeautifulSoup


def create_team_df(table):
    
    first_col = table['Unnamed: 0_level_0']['Starters'].drop(5)
    stats_cols = table['Basic Box Score Stats'].drop(5).replace({'Did Not Play': 0, 'Not With Team': 0, 'Did Not Dress': 0, np.nan: 0})
    
    name_cols = ['Player'] + [col for col in stats_cols] 
    data = {}
    for idx in range(len(name_cols)):
        if idx == 0:
            data[name_cols[idx]] =  first_col.tolist()
        else:
            c = stats_cols[name_cols[idx]].tolist()
            data[name_cols[idx]] = c
    
    return pd.DataFrame(data)


def scrape_games_date(url, month, day, year):
  
    # SCRAPE FROM URL
    html = urlopen(url + f'/boxscores/?month={month}&day={day}&year={year}').read()
    soup = BeautifulSoup(html, features="lxml")

    # GET GAMES LIST
    games = soup.find_all('div', attrs={'class':'game_summaries'})[0].find_all('p')
    g_list = list(games)

    # GET LINKS TO BOXSCORES LIST
    boxscore_list = []
    for idx in range(len(g_list)):
        h_list = g_list[idx].find_all('a', href=True)
        bs_link = url + h_list[0]['href']
        boxscore_list.append(bs_link)
  
    # CREATE STATS DATAFRAME
    stats = pd.DataFrame()
    for i in range(len(boxscore_list)):
        html_temp = urlopen(boxscore_list[i]).read()
        soup_temp = BeautifulSoup(html_temp, features="lxml")
        teams_names = (
            soup_temp.find_all('div', attrs={'class':'scorebox'})[0].find_all('a', {'href': re.compile(r'teams/')})[0].getText(), # away team
            soup_temp.find_all('div', attrs={'class':'scorebox'})[0].find_all('a', {'href': re.compile(r'teams/')})[1].getText()  # home team
        )

        scores = (
            soup_temp.find_all('div', attrs={'class':'scorebox'})[0].find_all('div', attrs={'class':'scores'})[0].find_all('div', attrs={'class':'score'})[0].getText(),
            soup_temp.find_all('div', attrs={'class':'scorebox'})[0].find_all('div', attrs={'class':'scores'})[1].find_all('div', attrs={'class':'score'})[0].getText()
        )

        tables = pd.read_html(boxscore_list[i])

        home_team = create_team_df(tables[len(tables)//2])
        home_team.drop(home_team.tail(1).index,inplace=True) # drop totals row
        h_name_s = pd.Series([teams_names[1]] * len(home_team))
        home_team.insert(1, 'Team', h_name_s)

        away_team = create_team_df(tables[0])
        away_team.drop(away_team.tail(1).index,inplace=True) # drop totals row
        a_name_s = pd.Series([teams_names[0]] * len(away_team))
        away_team.insert(1, 'Team', a_name_s)

        stats = pd.concat([stats, home_team])
        stats = pd.concat([stats, away_team])
        print(f'Game {i+1}: {teams_names[0]}  {scores[0]} - {scores[1]}  {teams_names[1]}')

    stats = stats.reset_index().drop('index', axis=1)

    # DATA TYPES CASTING
    stats['MP'] = stats['MP'].str.replace(':', '.')
    numeric_cols = [c for c in stats.columns if c != 'Player' and c != 'Team']
    for nc in numeric_cols:
        stats[nc] = pd.to_numeric(stats[nc])
    
    return stats