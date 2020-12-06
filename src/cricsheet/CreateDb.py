from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

#from cricSheet.io.MatchClass import Match


import yaml
import glob


class Match():

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.match_id = self.yaml_file.split("/")[-1].split("\\")[-1].split(".")[0]
        self.raw_data = None
        self.meta = None
        self.balldata = None
        
    def __str__(self):
        return f'Match_ID: {self.match_id}'

    def read_yaml(self, yaml_file):
        # load yaml contents
        with open(yaml_file, 'r') as stream:
            try:
                data = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        return data
    
    def execute(self):
        
        data = self.read_yaml(self.yaml_file)
        self.meta = self.parse_metadata(data)
        #self.balldata = parse_balldata(data)
    
    def parse_metadata(self, data):
        # TODO: subclass of main Match class: MetaData Class. Store as attributes of the class instead of dict
        # TODO: list of required columns, read and add to dict in one go. likewise optional columns with None if not present

        meta = data['info']
        d_meta = dict()
        
        d_meta['match_id'] = self.match_id
        d_meta['match_type'] = meta['match_type']
        d_meta['date_start'] = meta['dates'][0] # first entry in dates field - first day of match if Test, match date otherwise
        d_meta['gender'] = meta['gender']
        
        if 'competition' in meta:
            d_meta['competition'] = meta['competition']
        else:
            d_meta['competition'] = None
        
        d_meta['venue'] = meta['venue']
        
        if 'city' in meta:
            d_meta['city'] = meta['city']
        else:
            d_meta['city'] = None
            
        if 'overs' in meta:
            d_meta['overs'] = meta['overs']
        else:
            d_meta['overs'] = None
            
        d_meta['team_a'], d_meta['team_b'] = meta['teams']
        d_meta['toss_decision'] = meta['toss']['decision']
        d_meta['toss_winner'] = meta['toss']['winner']
        
        if 'winner' in meta['outcome']:
            d_meta['outcome'] = 'won'
            d_meta['outcome_winner'] = meta['outcome']['winner']
            d_meta['outcome_by_type'], d_meta['outcome_by_value'] = next(iter(meta['outcome']['by'].items()))
        else:
            d_meta['outcome'] = meta['outcome']['result']
            d_meta['outcome_winner']= None
            d_meta['outcome_by_type']= None
            d_meta['outcome_by_value']= None
       
        # didn't parse: umpires, player of match, data_verison, created_date, revision_number

        return d_meta
#%%

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
    


#%%

engine = create_engine('sqlite:///Data/sqlite/cricsheet_v2.db', echo=False)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


#%%


def load_metadata_to_db(match):    
    # load into DB
    session = Session()

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
    
#%%


data_files = glob.glob('Data/yaml/2020_male/*.yaml')

for file in data_files:
    match = Match(file)
    print(match)
    match.execute()
    
    load_metadata_to_db(match)

#%%

#match = Match("C:/Users/Adam/Documents/PycharmProjects/cricSheet/Data/yaml/recently_played_7_male/1207788.yaml")
#match.execute()



#%%

# session = Session()

# match_table = MatchTable()
# match_table.matchid = match.meta['match_id']
# match_table.match_type = match.meta['match_type']
# match_table.date_start = match.meta['date_start']
# match_table.gender = match.meta['gender']
# match_table.competition = match.meta['competition']
# match_table.venue =match.meta['venue']
# match_table.city = match.meta['city']
# match_table.overs = match.meta['overs']
# match_table.team_a = match.meta['team_a']
# match_table.team_b = match.meta['team_b']
# match_table.toss_decision = match.meta['toss_decision']
# match_table.toss_winner = match.meta['toss_winner']
# match_table.outcome = match.meta['outcome']
# match_table.outcome_winner = match.meta['outcome_winner']
# match_table.outcome_by_type = match.meta['outcome_by_type']
# match_table.outcome_by_value = match.meta['outcome_by_value']

# session.add(match_table)
# session.commit()


# session.close()
