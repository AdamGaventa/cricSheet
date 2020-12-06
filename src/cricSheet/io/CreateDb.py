from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

#from cricSheet.io.MatchClass import Match

"""
Class to read individual match yaml files

Design:
Methods:
    initialise
    read yaml
    parse yaml
    insert into db

Call as follows:

def read_single_match(matchFile.yaml)
    match = Match(matchFile.yaml)
    match_info = match.metadata()
    # add match metadata to match_master table

    match_details = match.ballByBall()
    # add match ball-by-ball to matches table


def read_all_matches(matchFolder)
    for matchFile in matchFolder:
        read_single_match(matchFile)

# add logging
"""
import yaml

Base = declarative_base()

class MatchTable(Base):
    __tablename__ = "match_master"
    
    matchid = Column(Integer,primary_key=True)
    match_type = Column(String,nullable=False)
    date_start = Column(String,nullable=False) # string for now, TODO: change to date
    gender = Column(String,nullable=False)
    competition = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    city = Column(String, nullable=True)
    overs = Column(Integer, nullable=True)
    team_a = Column(String, nullable=False)
    team_b = Column(String, nullable=False)
    toss_decision = Column(String, nullable=False)
    toss_winner = Column(String, nullable=False)
    outcome = Column(String, nullable=False)
    outcome_winner = Column(String, nullable=True)
    outcome_by_type = Column(String, nullable=True)
    outcome_by_value = Column(String, nullable=True)
    

engine = create_engine('sqlite:///cricsheet_v6.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

session = Session() 

match = Match("C:/Users/Adam/Documents/PycharmProjects/cricSheet/Data/yaml/recently_played_7_male/1207788.yaml")
match.execute()
#metadata = match.meta

match_table = MatchTable()
match_table.matchid = match.meta['match_id']
match_table.match_type = match.meta['match_type']
match_table.date_start = match.meta['date_start']
match_table.gender = match.meta['gender']
match_table.competition = match.meta['competition']
match_table.venue =match.meta['venue']
match_table.city = match.meta['city']
match_table.overs = match.meta['overs']
match_table.team_a = match.meta['team_a']
match_table.team_b = match.meta['team_b']
match_table.toss_decision = match.meta['toss_decision']
match_table.toss_winner = match.meta['toss_winner']
match_table.outcome = match.meta['outcome']
match_table.outcome_winner = match.meta['outcome_winner']
match_table.outcome_by_type = match.meta['outcome_by_type']
match_table.outcome_by_value = match.meta['outcome_by_value']

session.add(match_table)
session.commit()


session.close()
