import pandas as pd
import glob
import os
import re
import time
import logging

log = logging.getLogger(__name__)

from cricsheet.utils import fuzzy_match
from cricsheet.fow_analysis.collapses.extract_collapses import return_collapses


def get_files(filepath_fow, filepath_scores):

    log.debug('Getting scorecards')
    all_scores = glob.glob(os.path.join(filepath_scores, "*.csv"))
    all_scores_to_load = all_scores[:100]

    log.debug('Getting Fall of Wickets')
    all_fow = glob.glob(os.path.join(filepath_fow, "*.csv"))
    all_fow_to_load = all_fow[:100]

    return all_fow_to_load, all_scores_to_load

def join_scorecard_data(df_fow, df_scores):

    l_innings = []

    for innings in df_fow.MatchInnings.unique():
        log.debug('Joining scorecard to fow for innings: {innings}')

        df_fow_innings = df_fow[df_fow.MatchInnings == innings]
        df_scores_innings = df_scores[df_scores.MatchInnings == innings]

        # fuzzy match on Player
        log.debug('Fuzzy matching on player name')
        df_matched_innings = fuzzy_match(df_fow_innings, df_scores_innings, 'Player', 'Player')

        # merge cols from scores
        log.debug('Merging scorecard data')
        df_merged_innings = df_matched_innings.merge(df_scores_innings,
                                                     how='left',
                                                     left_on=['MatchId', 'MatchInnings', 'Team', 'TeamInnings', 'best'],
                                                     right_on=['MatchId', 'MatchInnings', 'Team', 'TeamInnings',
                                                               'Player']
                                                     )

        # reformat
        log.debug('Reformatting merged data')
        df_merged_innings.drop(['Player_x', 'Player_y'], axis=1, inplace=True)
        df_merged_innings = df_merged_innings.rename({'best': 'Player'}, axis=1)
        df_merged_innings['Player'] = df_merged_innings['Player'].apply(lambda x: re.sub('[!,*)@#%(&$_?.^†]', '', x))

        l_innings.append(df_merged_innings)

    log.debug('Combine all innings data for the match')
    df_merged_match = pd.concat(l_innings)

    return df_merged_match

def load_all_and_process():

    log.debug('Loading all files')
    filepath_fow = '../data/raw/csv/howstat/fall_of_wickets/'
    filepath_scores = '../data/raw/csv/howstat/scorecards/'

    all_fow_to_load, all_scores_to_load  = get_files(filepath_fow, filepath_scores)

    l_merged_df = []

    # for each fow file:
    for i in range(len(all_fow_to_load)):

        # read fow, read scorecard
        log.debug('Reading fall of wickets')
        df_fow = pd.read_csv(all_fow_to_load[i], index_col=0, parse_dates=[2], infer_datetime_format=True)
        log.debug('Reading scorecard')
        df_scores = pd.read_csv(all_scores_to_load[i], index_col=0, parse_dates=[2], infer_datetime_format=True)

        # select cols in scorecard, rename
        log.debug('Reformatting scorecard in preparation for joining')
        df_scores = df_scores[['MatchId', 'MatchInnings', 'Team', 'TeamInnings', 'Player', 'R', 'BF']]
        df_scores['BattingPosition'] = df_scores.groupby(['MatchId', 'MatchInnings', 'Team']).cumcount() + 1

        log.debug('Joining scorecard to fow ')
        df_merged_match = join_scorecard_data(df_fow, df_scores)
        l_merged_df.append(df_merged_match)

    log.debug('Combining all processed match data')
    df_processed_fow = pd.concat(l_merged_df)

    return df_processed_fow



def main():
    log.info('Processing data')
    df_processed_fow = load_all_and_process()

    log.info('Extracting collapses from fall of wickets data)
    df_collapses = df.groupby(['MatchId', 'MatchInnings', 'Team']).apply(return_collapses).reset_index()

    log.info('Saving to file')
    df_grouped.to_csv('../data/processed/collapses/all_collapses.csv')


if __name__ == "__main__":
    main()





