import urllib
import re
import pandas as pd
import numpy as np

from dateutil.parser import parse
from bs4 import BeautifulSoup


def parse_match_info(soup):
    match_info_data = np.array([item.text.strip() for item in soup.find_all(class_="TextBlack8")])[:5]
    match_info_category = np.array([item.text.strip() for item in soup.find_all(class_="TextBlackBold8")])[:5]

    d_match_info = pd.DataFrame(match_info_data, match_info_category).T.to_dict(orient='records')[0]
    d_match_info['Match Date:'] = parse(d_match_info['Match Date:']).date()
    # print(d_match_info)

    return d_match_info


def parse_scorecard(innings_section):
    """
    Takes a section of html containing the start of a scorecard, and builds a scorecard df upto and including the innings total.

    innings_section: bs4 object, which is of TextBlackBold8 class and contains the word "Innings" in its text.
    returns:  df of scorecard, and innings name as string
    """
    # The first parent is the header row of the scorecard
    headers = [x.text.replace('\xa0', ' ').strip() for x in innings_section.parent.find_all('td')]

    # We now want to loop through the siblings of the header row to get each batsman's scores, until we find the Total row,
    # at which point we append the row then terminate.
    nextNode = innings_section.parent
    data = []
    while True:
        nextNode = nextNode.find_next_sibling()  # use find_next_sibling() instead of next_sibling to avoid line breaks
        row = [x.text.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip() for x in nextNode.find_all('td')]

        if 'Total' in row:
            data.append(row)
            break
        else:
            data.append(row)

    innings_name = headers.pop(0).split('Innings')[0].strip()
    headers.insert(0, 'Details')
    headers.insert(0, 'Player')
    df_scorecard = pd.DataFrame(data, columns=headers)

    return innings_name, df_scorecard


def parse_fall_of_wickets(fow_section):
    """
    Takes a section of html containing the start of a fall of wickets section, and reads & reformats the FoW table.

    fow_section: bs4 object, a td element containing the words "Fall of Wickets"
    returns: df of fall of wickets
    """

    table = fow_section.parent.find('table')  # Move up one level and select table
    td = table.find_all('td')  # get table data
    tab = []

    for x in td:
        d_row = {}
        row = x.text.strip().replace(u'\xa0', u' ')
        row = row.split(' ')
        score = row[0].split('-')
        d_row['Wicket'] = score[0]
        d_row['Runs'] = score[1]
        d_row['Player'] = row[-1]
        tab.append(d_row)

    df_fow = pd.DataFrame(tab)

    return df_fow


def clean_scorecards(d_scorecards, d_match_info, l_innings):
    # Combine scorecards dfs, add key column from the dict
    df = pd.concat(d_scorecards, keys=l_innings).reset_index()

    # Expand key column into Team, Innings columns. Add Date column.
    meta = df.level_0.str.rsplit(n=1, expand=True)
    df[['Team', 'Innings']] = meta
    df = df.drop(['level_0'], axis=1)
    df['MatchDate'] = d_match_info['Match Date:']

    # Clean up column names and order
    cols = list(df.columns)
    cols = ['ScorecardIdx' if col == "level_1" else col for col in cols]
    df.columns = cols
    cols.insert(0, cols.pop(-2))
    cols.insert(0, cols.pop(-2))
    cols.insert(0, cols.pop(-1))
    df = df[cols]

    # Clean up data types
    cols_numeric = ['ScorecardIdx', 'R', 'BF', '4s', '6s', 'SR']
    df[cols_numeric] = df[cols_numeric].apply(pd.to_numeric, errors='coerce')
    df['MatchDate'] = df['MatchDate'].apply(pd.to_datetime, errors='coerce', yearfirst=True)

    return df


def clean_fow(d_fow, d_match_info, l_innings):
    # Combine scorecards dfs, add key column from the dict
    df = pd.concat(d_fow, keys=l_innings).reset_index()

    # Expand key column into Team, Innings columns. Add Date column.
    meta = df.level_0.str.rsplit(n=1, expand=True)
    df[['Team', 'Innings']] = meta
    df = df.drop(['level_0', 'level_1'], axis=1)
    df['MatchDate'] = d_match_info['Match Date:']

    # Clean up column names and order
    cols = list(df.columns)
    cols.insert(0, cols.pop(-2))
    cols.insert(0, cols.pop(-2))
    cols.insert(0, cols.pop(-1))
    df = df[cols]

    # Clean up data types
    cols_numeric = ['Wicket', 'Runs']
    df[cols_numeric] = df[cols_numeric].apply(pd.to_numeric, errors='coerce')
    df['MatchDate'] = df['MatchDate'].apply(pd.to_datetime, errors='coerce', yearfirst=True)

    return df