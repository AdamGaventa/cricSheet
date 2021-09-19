import logging
import sys
from cricsheet.fow_analysis.collapses.pipeline import Pipeline

# log = logging.getLogger(__name__)


def main():
    pipe = Pipeline("data/")
    pipe.execute()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s]: %(asctime)s: %(message)s",
        # datefmt='%m-%d %H:%M',
        filename="../cricsheet/logs/processCollapses.log",
        filemode="w",
    )

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s: %(message)s')
    formatter = logging.Formatter("[%(levelname)-8s]: %(asctime)s: %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger("").addHandler(console)

    main()
