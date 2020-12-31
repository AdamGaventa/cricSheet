import re
import pandas as pd
import numpy as np
from dateutil.parser import parse
import logging
from cricsheet.io_html.BaseParser import BaseParser

# TODO: improve logging
# TODO: improve error catching

log = logging.getLogger(__name__)


class MatchParser(BaseParser):

    def __init__(self, match_id):
        # Override init method to use base Match url

        super(MatchParser, self).__init__()
        self.match_id = match_id
        base_url = 'http://howstat.com/cricket/Statistics/Matches/MatchScorecard.asp?MatchCode='
        self.url = base_url + str(self.match_id)

        self.match_info = None
        self.scorecards = None
        self.fall_of_wickets = None

        self.d_scorecards = None

    def __str__(self):
        # Override str method to show that this is a Match class
        return f'Match Parser Class for match_id: {self.match_id}'

    def parse_match_info(self, soup):
        """
        Method to parse match information from the html soup
        :param soup: bs4 soup object of match page
        :return: d_match_info: a dict of match information including Match Date
        """
        log.debug('Parsing Match Info Data')
        match_info_data = np.array([item.text.strip() for item in soup.find_all(class_="TextBlack8")])[:5]
        log.debug('Parsing Match Info Category')
        match_info_category = np.array([item.text.strip() for item in soup.find_all(class_="TextBlackBold8")])[:5]

        log.debug('Formatting Match Info')
        d_match_info = pd.DataFrame(match_info_data, match_info_category).T.to_dict(orient='records')[0]
        d_match_info['Match Date:'] = parse(d_match_info['Match Date:'], fuzzy=True).date()

        return d_match_info


    def parse_single_scorecard(self, innings_section):

        """
        Takes a section of html soup containing the start of a scorecard, and builds a scorecard df upto and including the innings total.

        :param innings_section: bs4 object: html element TextBlackBold8 class containing the word "Innings" in its text
        :return: innings_name: str, containing name of innings in the form "{Team} {# innings}"
        :return: df_scorecard: pandas df, containing a scorecard of a single innings
        """
        # The first parent is the header row of the scorecard
        l_headers = [x.text.replace('\xa0', ' ').strip() for x in innings_section.parent.find_all('td')]

        # We now want to loop through the siblings of the header row to get each batsman's scores (and append the batsman score row to the data list),
        # until we find the Total row, at which point we append the Total row then terminate.
        next_node = innings_section.parent
        l_data = []
        while True:
            next_node = next_node.find_next_sibling()  # use find_next_sibling() instead of next_sibling to avoid line breaks
            row = [x.text.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip() for x in
                   next_node.find_all('td')]

            if 'Total' in row:
                l_data.append(row)
                break
            else:
                l_data.append(row)

        # Create output df from the list of data
        innings_name = l_headers.pop(0).split('Innings')[0].strip()
        l_headers.insert(0, 'Details')
        l_headers.insert(0, 'Player')
        df_scorecard = pd.DataFrame(l_data, columns=l_headers)

        return innings_name, df_scorecard

    def clean_single_scorecard(self, df_scorecard, team_innings, match_innings, d_match_info):
        """
        Method to clean each scorecard by summing cols, and adjusting d_types, and renaming cols

        :param d_scorecards: dict, containing scorecards of multiple innings, with keys as elements of l_innings
        :param d_match_info: dict, containing match information, in particular a MatchDate
        :return: df_clean_scorecards: pandas df, containing cleaned scorecards
        """
        df = df_scorecard.copy()
        cols = list(df.columns)

        # Rename index column and move to df column
        df.index = df.index.set_names(['ScorecardIdx'])
        df = df.reset_index()

        # Add metadata columns
        df['MatchId'] = self.match_id
        df['MatchDate'] = d_match_info['Match Date:']
        df['MatchInnings'] = match_innings
        df[['Team', 'TeamInnings']] = team_innings.rsplit(' ', 1)

        # Clean up data types
        df['MatchDate'] = df['MatchDate'].apply(pd.to_datetime, errors='coerce', yearfirst=True)
        df['% of Total'] = df['% of Total'].str.replace('%', '')
        cols_numeric = ['R', 'BF', '4s', '6s', 'SR', '% of Total']
        df[cols_numeric] = df[cols_numeric].apply(pd.to_numeric, errors='coerce')

        df = df.fillna(0)
        # Sum BF, 4s, 6s, and place into the appropriate place in the Totals row
        aggs = {'BF': 'sum', '4s': 'sum', '6s': 'sum'}
        df.loc[df.Player == 'Total', df.columns.isin(['BF', '4s', '6s'])] = list(df.iloc[:-1, :].agg(aggs))

        # Calculate innings strike rate
        df.loc[df.Player == 'Total', 'SR'] = df[df.Player == 'Total'].R / df[df.Player == 'Total'].BF * 100

        # Reorder columns
        cols = ['MatchId', 'MatchDate', 'MatchInnings', 'ScorecardIdx', 'Team', 'TeamInnings'] + cols
        df = df[cols]

        return df

    def parse_all_scorecards(self, soup, match_info):
        """
        Method to parse scorecards from a match url.
        Finds Innings sections, and parses the innings into a single df.

        :param soup: bs4 object, containing all html from a match url
        :return: df_scorecards: pandas df, containing all cleaned scorecards present at the match url
        :return: l_innings: list, containing the names (Team, #) of all innings present at the match url
        """
        # Loop through each TextBlackBold8 element
        # If the text contains the word 'Innings', the next section will be the innings scorecard: so parse it.
        d_scorecards = {}
        l_innings = []
        match_innings = 0
        for item in soup.find_all(class_="TextBlackBold8"):
            item_text = item.text.replace('\xa0', ' ').strip()
            if 'Innings' in item_text:
                match_innings += 1
                team_innings, df_scorecard = self.parse_single_scorecard(item)
                logging.debug(f'Parsed scorecard for: {team_innings} innings')

                df_scorecard_clean = self.clean_single_scorecard(df_scorecard, team_innings, match_innings, match_info)
                logging.debug(f'Cleaned scorecard for: {team_innings} innings')

                l_innings.append(team_innings)
                d_scorecards[team_innings] = df_scorecard_clean

        df_scorecards = pd.concat(d_scorecards, keys=l_innings).reset_index(drop=True)

        return df_scorecards, l_innings, d_scorecards


    def parse_single_fall_of_wickets(self, fow_section):
        """
        Takes a section of html containing the start of a fall of wickets section, and reads the FoW table.

        :param fow_section:  bs4 object, a td element containing the words "Fall of Wickets"
        :return: df_fow: pandas df, containing the fall of wickets for a single innings
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

    def clean_fall_of_wickets(self, d_fow, d_match_info, l_innings):
        """
        Method to convert the dictionary of fall of wickets into a pandas df, and clean by adding metadata, and adjusting d_types

        :param d_fow: containing fall of wickets of multiple innings, with keys as elements of l_innings
        :param d_match_info: dict, containing match information, in particular a MatchDate
        :param l_innings: list, containing the names of all innings present on the parsed webpage
        :return: df_clean_fow: pandas df, containing cleaned fall of wickets
        """
        # Combine scorecards dfs, add key column from the dict
        df = pd.concat(d_fow, keys=l_innings).reset_index()

        # Expand key column into Team, Innings columns. Add Date column. Add matchId column
        df['MatchId'] = self.match_id
        df['MatchDate'] = d_match_info['Match Date:']
        meta = df.level_0.str.rsplit(n=1, expand=True)
        df[['Team', 'Innings']] = meta
        df = df.drop(['level_0', 'level_1'], axis=1)

        # Clean up column names and order
        cols = list(df.columns)
        cols = cols[-4:] + cols[:-4]
        df = df[cols]

        # Clean up data types
        df['MatchDate'] = df['MatchDate'].apply(pd.to_datetime, errors='coerce', yearfirst=True)
        cols_numeric = ['Wicket', 'Runs']
        df[cols_numeric] = df[cols_numeric].apply(pd.to_numeric, errors='coerce')

        df_clean_fow = df.copy()

        return df_clean_fow

    def parse_all_fall_of_wickets(self, soup, l_innings):
        """

        :param soup: bs4 object, containing all html from a match url
        :param l_innings: list, containing the names (Team, #) of all innings present at the match url
        :return: pandas df, containing all cleaned fall of wickets present at the match url
        """
        # Loop through each Fall of Wickets section, and parse the FoW record.
        # Store in a dict with keys as innings names from parsed scorecard section.
        # This assumes there will always be a FoW for each scorecard
        l_fow = []
        fow_sections = soup.findAll("td", text=re.compile('Fall of Wickets'))
        for item in fow_sections:
            df_fow = self.parse_single_fall_of_wickets(item)
            l_fow.append(df_fow)
            logging.debug('Parsed FoW')

        # Convert list of FoW dfs to dict
        if len(l_fow) == len(l_innings):
            logging.debug(f'There are {len(l_fow)} innings with fall of wicket data')
            d_fow = {l_innings[i]: l_fow[i] for i in range(len(l_fow))}

            df = self.clean_fall_of_wickets(d_fow, self.match_info, l_innings)

            return df
        else:
            logging.warning('Number of innings does not match number of fall of wickets')  # TODO: raise error

    def execute(self):
        log.debug('Reading url')
        html_page = super().read_html()
        log.debug('Creating a beautiful soup')
        self.soup = super().create_soup(html_page)

        log.info(f'Parsing Match: {self.match_id}')

        log.debug('Parsing Match Info...')
        self.match_info = self.parse_match_info(self.soup)
        log.debug('Parsing Match Info...Complete!')

        log.debug('Parsing Scorecards...')
        self.scorecards, l_innings, self.d_scorecards = self.parse_all_scorecards(self.soup, self.match_info)  # l_innings required for FoW parsing, but not to keep as an attribute
        log.debug('Parsing Scorecards...Complete!')

        log.debug('Parsing Fall of Wickets...')
        self.fall_of_wickets = self.parse_all_fall_of_wickets(self.soup, l_innings)  # l_innings req., so always execute scorecard parsing first
        log.debug('Parsing Fall of Wickets..Complete!.')
