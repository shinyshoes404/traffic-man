import sqlalchemy as db
#from traffic_man import metadata_obj

metadata_obj = db.MetaData()

check_times = db.Table(
        'check_times',
        metadata_obj,
        db.Column('time_id', db.Integer, primary_key=True),
        db.Column('time', db.String(5), nullable=False)
)

holidays = db.Table(
        'holidays',
        metadata_obj,
        db.Column('holiday_id', db.Integer, primary_key=True),
        db.Column('date', db.String(10), nullable=False)
)

phone_numbers = db.Table(
        'phone_numbers',
        metadata_obj,
        db.Column('phone_num', db.String(12), primary_key=True),
        db.Column('origin_place_id', db.String(255), nullable=True),
        db.Column('dest_place_id', db.String(255), nullable=True),
        db.Column('status', db.String(15), nullable=False),
        db.Column('auth_status', db.String(10), nullable=False),
        db.Column('origin_place_id_confirmed', db.String(3), nullable=False),
        db.Column('dest_place_id_confirmed', db.String(3), nullable=False)

)

check_days = db.Table(
        'check_days',
        metadata_obj,
        db.Column('check_days', db.String(9), primary_key=True)
)

traffic_conditions = db.Table(
        'traffic_conditions',
        metadata_obj,
        db.Column('condition_id', db.Integer, primary_key=True),
        db.Column('date', db.String(10), nullable=False),
        db.Column('origin_place_id', db.String(255), nullable=True),
        db.Column('dest_place_id', db.String(255), nullable=True),
        db.Column('bad_traffic_datetime', db.String(16), nullable=False),
        db.Column('resolve_traffic_datetime', db.String(16), nullable=True)
)

traffic_data = db.Table(
        'traffic_data',
        metadata_obj,
        db.Column('traffic_data_id', db.Integer, primary_key=True),
        db.Column('datetime', db.String(16), nullable=False),
        db.Column('origin_place_id', db.String(255), nullable=False),
        db.Column('origin_addr', db.String(50), nullable=False),
        db.Column('dest_place_id', db.String(255), nullable=False),
        db.Column('destination_addr', db.String(50), nullable=False),
        db.Column('duration_sec', db.Integer, nullable=False),
        db.Column('duration_traffic_sec', db.Integer, nullable=False),
        db.Column('traffic_ratio', db.REAL, nullable=False)
)

sms_data = db.Table(
        'sms_data',
        metadata_obj,
        db.Column('sms_id', db.Integer, primary_key=True),
        db.Column('datetime', db.String(16), nullable=False),
        db.Column('sms_type', db.String(20), nullable=False),
        db.Column('status', db.String(10), nullable=False),
        db.Column('direction', db.String(10), nullable=False),
        db.Column('msg_content', db.String(160), nullable=False),
        db.Column('phone_num', db.String(12), nullable=False)
)

action_attempts = db.Table(
        'action_attempts',
        metadata_obj,
        db.Column('auth_id', db.Integer, primary_key=True),
        db.Column('datetime', db.String(16), nullable=False),
        db.Column('status', db.String(15), nullable=False),
        db.Column('phone_num', db.String(12), nullable=False)

)