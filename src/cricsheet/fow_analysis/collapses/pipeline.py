import pandas as pd
import glob
import os
import re
import logging

from cricsheet.utils import fuzzy_match
from cricsheet.fow_analysis.collapses.extract_collapses import return_collapses

log = logging.getLogger(__name__)


class Pipeline(object):

    # pd.read_csv(os.getcwd() + '/data/raw/csv/howstat/fall_of_wickets/fow_1.csv')

    def __init__(self, dir_data):

        self.dir_data = dir_data
        self.filepath_fow = dir_data + "/raw/csv/howstat/fall_of_wickets/"
        self.filepath_scores = dir_data + "/raw/csv/howstat/scorecards/"
        self.filepath_collapses = dir_data + "/processed/collapses/all_collapses.csv"

        # path to save results

    def get_filenames(self, filepath_fow, filepath_scores):

        log.debug("Getting Fall of Wickets")
        all_fow = glob.glob(os.path.join(filepath_fow, "*.csv"))
        l_fow_paths = all_fow[:]

        log.debug("Getting scorecards")
        all_scores = glob.glob(os.path.join(filepath_scores, "*.csv"))
        l_score_paths = all_scores[:]

        return l_fow_paths, l_score_paths

    def join_scorecard_data(self, df_fow, df_scores):

        l_innings = []
        for innings in df_fow.MatchInnings.unique():
            log.debug(f"Joining scorecard to fow for innings: {innings}")

            df_fow_innings = df_fow[df_fow.MatchInnings == innings]
            df_scores_innings = df_scores[df_scores.MatchInnings == innings]

            # fuzzy match on Player
            log.debug("Fuzzy matching on player name")
            df_matched_innings = fuzzy_match(
                df_fow_innings, df_scores_innings, "Player", "Player"
            )

            # merge cols from scores
            log.debug("Merging scorecard data")
            df_merged_innings = df_matched_innings.merge(
                df_scores_innings,
                how="left",
                left_on=["MatchId", "MatchInnings", "Team", "TeamInnings", "best"],
                right_on=["MatchId", "MatchInnings", "Team", "TeamInnings", "Player"],
            )

            # reformat
            log.debug("Reformatting merged data")
            df_merged_innings.drop(["Player_x", "Player_y"], axis=1, inplace=True)
            df_merged_innings = df_merged_innings.rename({"best": "Player"}, axis=1)
            df_merged_innings["Player"] = df_merged_innings["Player"].apply(
                lambda x: re.sub("[!,*)@#%(&$_?.^†]", "", x)
            )

            l_innings.append(df_merged_innings)

        log.debug("Combine all innings data for the match")
        df_merged_match = pd.concat(l_innings)

        return df_merged_match

    def preprocess_files(self, l_fow_paths, l_score_paths):

        l_merged_df = []
        # for each fow file:
        for i in range(len(l_fow_paths)):
            # read fow, read scorecard
            log.debug(f"Preprocess match: {l_fow_paths[i]}")

            log.debug("Reading fall of wickets")
            df_fow = pd.read_csv(
                l_fow_paths[i], index_col=0, parse_dates=[2], infer_datetime_format=True
            )
            log.debug("Reading scorecard")
            df_scores = pd.read_csv(
                l_score_paths[i],
                index_col=0,
                parse_dates=[2],
                infer_datetime_format=True,
            )

            # select cols in scorecard, rename
            log.debug("Reformatting scorecard in preparation for joining")
            df_scores = df_scores[
                ["MatchId", "MatchInnings", "Team", "TeamInnings", "Player", "R", "BF"]
            ]
            df_scores["BattingPosition"] = (
                df_scores.groupby(["MatchId", "MatchInnings", "Team"]).cumcount() + 1
            )

            log.debug("Joining scorecard to fow ")
            df_merged_match = self.join_scorecard_data(df_fow, df_scores)
            l_merged_df.append(df_merged_match)

        log.debug("Combining all processed match data")
        df_processed_fow = pd.concat(l_merged_df)

        return df_processed_fow

    def execute(self):

        log.info("Loading files")
        l_fow_paths, l_score_paths = self.get_filenames(
            self.filepath_fow, self.filepath_scores
        )

        log.info("Preprocessing data")
        df_processed_fow = self.preprocess_files(l_fow_paths, l_score_paths)

        log.info("Extracting collapses")
        df_collapses = (
            df_processed_fow.groupby(["MatchId", "MatchDate", "MatchInnings", "Team"])
            .apply(return_collapses)
            .reset_index()
        )

        # TODO: allow defining collapses here

        log.info("Saving to file")
        df_collapses.to_csv(self.dir_data + "/processed/collapses/all_collapses.csv")
