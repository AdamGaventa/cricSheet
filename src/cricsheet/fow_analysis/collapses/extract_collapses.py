import pandas as pd
from collections import namedtuple


def check_collapse_n_wickets(d_runs, n):
    """
    Takes a dictionary of wickets falling (runs for wicket i=1:10), and n a number of wickets fallen to define a collapse.
    Returns a list of all collapses for n number of wickets fallen.
    The list contains Collapse namedtuple: start wicket, end wicket of collapse, number of runs, and positions involved.
    """

    Collapse = namedtuple("Collapse", ["start", "end", "runs", "wickets_lost", "batters"])
    n_collapses = 0
    l_collapses = []

    for i in range(n, len(d_runs)):
        l_wickets_lost = []
        l_batters_involved = []

        # skip the case from 0 to i, since only i wickets will have fallen
        if i == n:
            continue

        # calculate runs lost for wicket # i-n, i-n+1,...,i
        # e.g. if n=2 and i=5, wickets 3,4,5 have fallen
        diff = d_runs[i][0] - d_runs[i - n][0]

        if diff <= 30:
            l_wickets_lost = [s for s in range(i - n, i + 1)]
            l_batters_involved = [d_runs[s][1] for s in range(i - n, i + 1)]
            collapse = Collapse(start=i - n, end=i, runs=diff, wickets_lost=l_wickets_lost,
                                batters=l_batters_involved)
            l_collapses.append(collapse)

    return l_collapses


def check_all_collapses(d_runs):
    """
    Go through all length batting collapses to see if any smaller are extended.
    e.g. lose 3 wickets for 30, lose 4 wickets for 30, lose 5 wickets for 30 -> only count as 1 collapse

    check if batters for small n is contained within batters for larger n

    do some optimisations at a later stage
    """
    # build list of collapses for every length of collapse (min.2, max.10 wickets lost)
    l_collapses = []
    for i in reversed(range(2, 10)):
        l_collapse = check_collapse_n_wickets(d_runs, i)
        if len(l_collapse) > 0:
            l_collapses += l_collapse

    # reduce to drop any "sub-collapses" e.g. 4,5,6 is a sub-collapse of 4,5,6,7
    l_collapses_reduced = l_collapses[:]
    for m in l_collapses:
        for n in l_collapses:
            if set(m.wickets_lost) <= set(n.wickets_lost) and m != n:
                # if is a sub-collapse, remove the smaller object from the list: we no longer need to test it
                l_collapses_reduced.remove(m)
                # and break, as
                break

    # return number of collapses
    return l_collapses_reduced


def return_collapses(df):
    """
    for each innings (group), want to return one row for each collapse,
    containing columns: start, end, runs, positions, (batters)

    intended to be applied to a groupby of FoW, such that each innings is a unique group
    """

    l_runs = list(df.Runs)
    l_runs.insert(0, 0)
    l_player = list(df.Player)
    l_player.insert(0, "")

    d_runs = {i: (l_runs[i], l_player[i]) for i in range(len(l_runs))}

    l_collapses = check_all_collapses(d_runs)

    return pd.DataFrame(l_collapses)