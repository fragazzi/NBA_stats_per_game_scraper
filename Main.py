import sys

from Utils import *


if __name__ == '__main__':
    URL = 'https://www.basketball-reference.com'
    
    date = sys.argv[1:][0]
    tokens = date.split('/')
      
    DAY, MONTH, YEAR = tokens[0], tokens[1], tokens[2]
    
    print('Scraping games stats of {}...'.format(date))

    try:
        stats = scrape_games_date(URL, MONTH, DAY, YEAR)
        print('Ready!')

        print('-' * 35)
        print('TOP 10 ASSIST')
        print(stats.sort_values('AST', ascending=False).iloc[0:10][['Player', 'AST']])
        print('-' * 35)
        print('TOP 10 REBOUND')
        print(stats.sort_values('TRB', ascending=False).iloc[0:10][['Player', 'TRB']])
        print('-' * 35)
        print('TOP 10 STEALS')
        print(stats.sort_values('STL', ascending=False).iloc[0:10][['Player', 'STL']])
        print('-' * 35)
        print('TOP 10 BLOCKS')
        print(stats.sort_values('BLK', ascending=False).iloc[0:10][['Player', 'BLK']])
        
        # IF YOU WANT TO SAVE THE STATS
        # stats.to_csv(f'stats_{DAY}_{MONTH}_{YEAR}.csv')
        
    except:
        print('Scraping error!')
        print('Maybe... Wrong date?')
