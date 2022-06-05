from traffic_man.models import metadata_obj, db, check_times, check_days, holidays, phone_numbers, check_days, traffic_conditions, traffic_data

engine = db.create_engine('sqlite:///traffic_man.db')


metadata_obj.create_all(engine)

inspector = db.inspect(engine)

print(inspector.get_table_names())
