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
        
        #self.raw_data = data
        return data
    
    def execute(self):
        
        data = self.read_yaml(self.yaml_file)
        self.meta = self.parse_metadata(data)
        self.balldata = self.parse_ball_by_ball(data)
    
    def parse_metadata(self, data):
        # TODO: subclass of main Match class: MetaData Class. Store as attributes of the class instead of dict
        # TODO: list of required columns, read and add to dict in one go. likewise optional columns with None if not present

        meta = data['info']
        d_meta = dict()
        
        d_meta['match_id'] = self.match_id
        d_meta['match_type'] = meta['match_type']
        d_meta['date_start'] = meta['dates'][0] # first entry in dates field - first day of match if Test, match date otherwise
        d_meta['gender'] = meta['gender']
        d_meta['competition'] = meta['competition'] if 'competition' in meta else None
        d_meta['venue'] = meta['venue']
        d_meta['city'] = meta['city'] if 'city' in meta else None
        d_meta['overs'] = meta['overs'] if 'overs' in meta else None
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

    def parse_ball_by_ball(self, data):
        # TODO: subclass of main Match class: MetaData Class. Store as attributes of the class instead of dict
        # TODO: list of required columns, read and add to dict in one go. likewise optional columns with None if not present

        balldata = data['innings']
        d_ball = dict()

        d_ball['match_id'] = self.match_id
        #d_ball['match_type'] = balldata['match_type']

        for inning in balldata:
            innings_name = list(inning.keys())[0]
            d_ball['innings'] = innings_name
            d_ball['team'] = inning[innings_name]['team']
            
            deliveries = inning[innings_name]['deliveries']
            #for delivery in deliveries:
            
            # for each delivery in deliveries:
            #     over #
            #     ball_in_over #
            #     ball counter?
            #     batsman
            #     bowler
            #     non-striker
            #     runs_batsman
            #     runs_extras
            #     runs_total
            #     extras_type
            #     extras_value
            #     batsman score counter?
            #     innings score counter?
            #     bowler balls bowled counter?
            #     bowler runs conceded counter?
            #     wicket (True/False)
            #     wicket_player_out
            #     wicket_fielder
            #     wicket_kind
                


        return d_ball

#=============================================================================
# # from https://github.com/aadiuppal/cricsheet_db/blob/master/yaml_read.py
#     def getBallDetails(self,myfile):
#         stream = file(myfile,'r')
#         balls_data = []
#         matchid = get_id(myfile)
#         data = yaml.load(stream)
#         #print data.keys()
#         for i in range(len(data['innings'])):
#             innings = data['innings'][i].keys()[0]
#             batting_team = data['innings'][i][innings]['team']
#             for j in range(len(data['innings'][i][innings]['deliveries'])):
#                 ball_num = j+1
#                 over,batsman,bowler,non_striker,runs_batsman,runs_extras,runs_total,wicket_player,wicket_kind,wicket_fielder = self.get_ball_data(data['innings'][i][innings]['deliveries'][j])
#                 balls_data.append([matchid,innings,batting_team,ball_num,over,batsman,
#                     bowler,non_striker,runs_batsman,runs_extras,runs_total,wicket_player,wicket_kind,wicket_fielder])
#         #print data['innings'][0]['1st innings']['deliveries'][0]
#         #print data['innings'][0]['1st innings']['team']
#         return balls_data

#     def get_ball_data(self,dat):
#         over = dat.keys()[0]
#         batsman = dat[over]['batsman']
#         bowler = dat[over]['bowler']
#         non_striker = dat[over]['non_striker']
#         runs_batsman = dat[over]['runs']['batsman']
#         runs_extras = dat[over]['runs']['extras']
#         runs_total = dat[over]['runs']['total']
#         if 'wicket' in dat[over]:
#             wicket_player = dat[over]['wicket']['player_out']
#             wicket_kind = dat[over]['wicket']['kind']
#             if 'fielders' in dat[over]['wicket']:
#                 wicket_fielder = dat[over]['wicket']['fielders'][0]
#             else:
#                 wicket_fielder = None
#         else:
#             wicket_fielder,wicket_kind,wicket_player = None,None,None
#         return [over,batsman,bowler,non_striker,runs_batsman,runs_extras,runs_total,wicket_player,wicket_kind,wicket_fielder]
# #=============================================================================
