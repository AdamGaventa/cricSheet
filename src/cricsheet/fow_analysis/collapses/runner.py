import logging
from cricsheet.fow_analysis.collapses.pipeline import Pipeline

log = logging.getLogger(__name__)

def main():
    pipe = Pipeline('data/')
    pipe.execute()

if __name__ == "__main__":
    main()
