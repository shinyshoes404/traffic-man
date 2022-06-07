import sqlalchemy as db

metadata_obj = db.MetaData()
engine = db.create_engine('sqlite:///traffic_man.db')
metadata_obj.create_all(engine)