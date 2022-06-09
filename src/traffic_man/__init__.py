import sqlalchemy as db
from traffic_man.config import Config
from traffic_man.models import metadata_obj

engine = db.create_engine('sqlite:///' + Config.db_path)
metadata_obj.create_all(engine)