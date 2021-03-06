#%%
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cricsheet.io_xml.models import Base
from cricsheet.io_xml.cricsheet_xml_reader import CricsheetXMLReader

import time
import logging

start_time = time.time()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

#if __name__ == '__main__':
engine = create_engine('sqlite:///../../../data/preprocessed/sqlite/cricsheet_xml.db', echo=False)
#engine = create_engine('sqlite:///../../../data/preprocessed/sqlite/cricsheet_xml_test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
reader = CricsheetXMLReader()

objects = reader.get_objects_from_directory('../../../data/raw/xml/')
#objects = reader.get_objects_from_directory('../../../data/test/')

end_parse_time = time.time()
print(f'{end_parse_time - start_time} seconds')

#%%
#import pickle

#pickle.dump(objects, open( "parsedXML.p", "wb" ))
#objects = pickle.load( open( "parsedXML.p", "rb" ) )
            
#%%
session.bulk_save_objects(objects)
session.commit()
session.close()

end_db_creation_time = time.time()
print(f'{end_db_creation_time - end_parse_time} seconds')

#%%
