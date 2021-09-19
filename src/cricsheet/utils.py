from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import difflib
from functools import partial

import logging

log = logging.getLogger(__name__)


def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=1):
    """
    Using fuzzy wuzzy

    :param df_1: the left table to join
    :param df_2: the right table to join
    :param key1: key column of the left table
    :param key2: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with boths keys and matches

    """
    s = df_2[key2].tolist()

    m = df_1[key1].apply(
        lambda x: process.extract(x, s, limit=limit, scorer=fuzz.partial_ratio)
    )
    df_1["matches"] = m

    m2 = df_1["matches"].apply(
        lambda x: ", ".join([i[0] for i in x if i[1] >= threshold])
    )
    df_1["matches"] = m2

    return df_1


def fuzzy_match(df1, df2, left_on, right_on):
    """
    using difflib

    Args:
        df1:
        df2:
        left_on:
        right_on:

    Returns:

    """
    f = partial(
        difflib.get_close_matches, possibilities=df2[right_on].tolist(), n=2, cutoff=0.3
    )

    matches = df1[left_on].map(f).str[0].fillna("")
    scores = [
        difflib.SequenceMatcher(None, x, y).ratio()
        for x, y in zip(matches, df1[left_on])
    ]

    df_fuzzy_matched = df1.assign(best=matches, score=scores)

    return df_fuzzy_matched
