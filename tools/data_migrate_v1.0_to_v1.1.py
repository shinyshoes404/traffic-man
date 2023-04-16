
import os, sys
import sqlalchemy as db 

print("############ Traffic Man Data Migration Script #################")
print("############        v1.0.0 --> v1.1.0          #################")
print("")
print("What is the absolute path to the v1.0.0 sqlite database file?")
db_path_1_0 = input()

if not os.path.isfile(db_path_1_0):
    print("ERROR: That file doesn't exist. Double check your file path.")
    sys.exit(1)


########################################## v1.0.0 database ######################################################
metadata_obj_1_0 = db.MetaData()

check_times_1_0 = db.Table(
        'check_times',
        metadata_obj_1_0,
        db.Column('time_id', db.Integer, primary_key=True),
        db.Column('time', db.String(5), nullable=False)
)

holidays_1_0 = db.Table(
        'holidays',
        metadata_obj_1_0,
        db.Column('holiday_id', db.Integer, primary_key=True),
        db.Column('date', db.String(10), nullable=False)
)

phone_numbers_1_0 = db.Table(
        'phone_numbers',
        metadata_obj_1_0,
        db.Column('phone_num', db.String(12), primary_key=True),
        db.Column('origin_place_id', db.String(255), nullable=True),
        db.Column('dest_place_id', db.String(255), nullable=True),
        db.Column('status', db.String(15), nullable=False),
        db.Column('auth_status', db.String(10), nullable=False)

)

check_days_1_0 = db.Table(
        'check_days',
        metadata_obj_1_0,
        db.Column('check_days', db.String(9), primary_key=True)
)

traffic_conditions_1_0 = db.Table(
        'traffic_conditions',
        metadata_obj_1_0,
        db.Column('condition_id', db.Integer, primary_key=True),
        db.Column('date', db.String(10), nullable=False),
        db.Column('origin_place_id', db.String(255), nullable=True),
        db.Column('dest_place_id', db.String(255), nullable=True),
        db.Column('bad_traffic_datetime', db.String(16), nullable=False),
        db.Column('resolve_traffic_datetime', db.String(16), nullable=True)
)

traffic_data_1_0 = db.Table(
        'traffic_data',
        metadata_obj_1_0,
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

sms_data_1_0 = db.Table(
        'sms_data',
        metadata_obj_1_0,
        db.Column('sms_id', db.Integer, primary_key=True),
        db.Column('datetime', db.String(16), nullable=False),
        db.Column('sms_type', db.String(20), nullable=False),
        db.Column('status', db.String(10), nullable=False),
        db.Column('direction', db.String(10), nullable=False),
        db.Column('msg_content', db.String(160), nullable=False),
        db.Column('phone_num', db.String(12), nullable=False)
)

action_attempts_1_0 = db.Table(
        'action_attempts',
        metadata_obj_1_0,
        db.Column('auth_id', db.Integer, primary_key=True),
        db.Column('datetime', db.String(16), nullable=False),
        db.Column('status', db.String(15), nullable=False),
        db.Column('phone_num', db.String(12), nullable=False)

)

engine_1_0 = db.create_engine('sqlite:///' + db_path_1_0)


########################################### v1.1.0 database ####################################################
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

try:
    db_path_1_1 = os.path.abspath(os.path.dirname(__file__))
    db_path_1_1 = os.path.join(db_path_1_1, "traffic_man_v1_1.db")
    engine_1_1 = db.create_engine('sqlite:///' + db_path_1_1)
    metadata_obj.create_all(engine_1_1)
except Exception as e:
    print("ERROR: Problem creating v1.1.0 database file.")
    print("db path: {0}".format(db_path_1_1))
    print(e)
    sys.exit(1)

############################################### Data migration ##############################################
# No need to worry about migrating check_days, holidays, or check_times, becasue those repopulate every time traffic-man restarts
# action_attempts is not present in the v1.1.0 data model. No need to bring any data over.



########################### phone_numbers #######################################3

# need to add data to non nullable columns origin_place_id_confirmed and dest_place_id_confirmed

try:
    qry_phone_nums = phone_numbers_1_0.select()
    with engine_1_0.connect() as connection:
        res_obj = connection.execute(qry_phone_nums)
        phone_num_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Failed to extract exising phone numbers.")
    print(e)
    sys.exit(1)

# add the correct value to the new columns before inserting int the v1.1.0 database
phone_num_data_1_1 = []
for rows in phone_num_data:
    temp_obj = {}
    temp_obj["phone_num"] = rows[0]
    temp_obj["origin_place_id"] = rows[1]
    temp_obj["dest_place_id"] = rows[2]
    temp_obj["status"] = rows[3]
    temp_obj["auth_status"] = rows[4]
    if rows[1] and rows[3] != "needs setup":
        temp_obj["origin_place_id_confirmed"] = "yes"
    else:
        temp_obj["origin_place_id_confirmed"] = "no"
    if rows[2] and rows[3] != "needs setup":
        temp_obj["dest_place_id_confirmed"] = "yes"
    else:
        temp_obj["dest_place_id_confirmed"] = "no"
    
    phone_num_data_1_1.append(temp_obj.copy())

# add data to v1.1.0 database
try:
    qry_phone_nums_insert = phone_numbers.insert(phone_num_data_1_1)
    with engine_1_1.connect() as connection:
        connection.execute(qry_phone_nums_insert)
except Exception as e:
    print("ERROR: Failed to insert phone number data.")
    print(e)
    sys.exit(1)

# fetch data to verify migration
try:
    qry_phone_num_verify = phone_numbers.select()
    with engine_1_1.connect() as connection:
        new_phone_num_res_obj = connection.execute(qry_phone_num_verify)
        new_phone_num_data = new_phone_num_res_obj.fetchall()
except Exception as e:
    print("ERROR: Problem fetching new phone number data")
    print(e)
    sys.exit(1)

## --------------------------- END phone_numbers ------------------------------------- ##


############################# traffic_conditions ########################################

try:
    qry = traffic_conditions_1_0.select()
    with engine_1_0.connect() as connection:
        res_obj = connection.execute(qry)
        traffic_cond_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Failed to extract exising traffic condition data.")
    print(e)
    sys.exit(1)

# add the correct value to the new columns before inserting int the v1.1.0 database
traffic_cond_data_1_1 = []
for rows in traffic_cond_data:
    temp_obj = {}
    temp_obj["condition_id"] = rows[0]
    temp_obj["date"] = rows[1]
    temp_obj["origin_place_id"] = rows[2]
    temp_obj["dest_place_id"] = rows[3]
    temp_obj["bad_traffic_datetime"] = rows[4]
    temp_obj["resolve_traffic_datetime"] = rows[5]
    
    traffic_cond_data_1_1.append(temp_obj.copy())

# add data to v1.1.0 database
try:
    qry_insert = traffic_conditions.insert(traffic_cond_data_1_1)
    with engine_1_1.connect() as connection:
        connection.execute(qry_insert)
except Exception as e:
    print("ERROR: Failed to insert traffic condition data.")
    print(e)
    sys.exit(1)

# fetch data to verify migration
try:
    qry_verify = traffic_conditions.select()
    with engine_1_1.connect() as connection:
        res_obj = connection.execute(qry_verify)
        new_traffic_cond_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Problem fetching new traffic condition data")
    print(e)
    sys.exit(1)

## --------------------------- END traffic_conditions ---------------------------------##

############################# traffic_data ########################################

try:
    qry = traffic_data_1_0.select()
    with engine_1_0.connect() as connection:
        res_obj = connection.execute(qry)
        traffic_res_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Failed to extract exising traffic data.")
    print(e)
    sys.exit(1)

# add the correct value to the new columns before inserting int the v1.1.0 database
traffic_data_1_1 = []
for rows in traffic_res_data:
    temp_obj = {}
    temp_obj["traffic_data_id"] = rows[0]
    temp_obj["datetime"] = rows[1]
    temp_obj["origin_place_id"] = rows[2]
    temp_obj["origin_addr"] = rows[3]
    temp_obj["dest_place_id"] = rows[4]
    temp_obj["destination_addr"] = rows[5]
    temp_obj["duration_sec"] = rows[6] 
    temp_obj["duration_traffic_sec"] = rows[7]  
    temp_obj["traffic_ratio"] = rows[8]


    traffic_data_1_1.append(temp_obj.copy())

# add data to v1.1.0 database
for data in traffic_data_1_1:
    try:
        qry_insert = traffic_data.insert(data)
        with engine_1_1.connect() as connection:
            connection.execute(qry_insert)
    except Exception as e:
        print("ERROR: Failed to insert traffic data.")
        print(e)
        sys.exit(1)

# fetch data to verify migration
try:
    qry_verify = traffic_data.select()
    with engine_1_1.connect() as connection:
        res_obj = connection.execute(qry_verify)
        new_traffic_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Problem fetching new traffic condition data")
    print(e)
    sys.exit(1)

## --------------------------- END traffic_data ---------------------------------##

############################# sms_data ########################################

try:
    qry = sms_data_1_0.select()
    with engine_1_0.connect() as connection:
        res_obj = connection.execute(qry)
        sms_res_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Failed to extract exising sms data.")
    print(e)
    sys.exit(1)

# add the correct value to the new columns before inserting int the v1.1.0 database
sms_data_1_1 = []
for rows in sms_res_data:
    temp_obj = {}
    temp_obj["sms_id"] = rows[0]
    temp_obj["datetime"] = rows[1]
    temp_obj["sms_type"] = rows[2]
    temp_obj["status"] = rows[3]
    temp_obj["direction"] = rows[4]
    temp_obj["msg_content"] = rows[5]
    temp_obj["phone_num"] = rows[6] 


    sms_data_1_1.append(temp_obj.copy())

# add data to v1.1.0 database
for data in sms_data_1_1:
    try:
        qry_insert = sms_data.insert(data)
        with engine_1_1.connect() as connection:
            connection.execute(qry_insert)
    except Exception as e:
        print("ERROR: Failed to insert sms data.")
        print(e)
        sys.exit(1)

# fetch data to verify migration
try:
    qry_verify = sms_data.select()
    with engine_1_1.connect() as connection:
        res_obj = connection.execute(qry_verify)
        new_sms_data = res_obj.fetchall()
except Exception as e:
    print("ERROR: Problem fetching new sms condition data")
    print(e)
    sys.exit(1)

## --------------------------- END sms_data ---------------------------------##




print("")
print("################## COMPLETE ##########################")
print("####### Find your v1.1.0 sqlite db file here #########")
print("")
print(db_path_1_1)
print("")
print("######################################################")

print("")
print("################### phone_numbers ####################")
print("v1.0.0 record count: {0}   v1.1.0 record count: {1}".format(len(phone_num_data), len(new_phone_num_data)))
print("")
print("--- Example data from v1.1.0 database ---")
for i in range(0,5):
    try:
        print(new_phone_num_data[i])
    except IndexError:
        pass
print("")

print("")
print("################ traffic_conditions #################")
print("v1.0.0 record count: {0}   v1.1.0 record count: {1}".format(len(traffic_cond_data), len(new_traffic_cond_data)))
print("")
print("--- Example data from v1.1.0 database ---")
for i in range(0,5):
    try:
        print(traffic_cond_data[i])
    except IndexError:
        pass
print("")

print("")
print("################ traffic_data #################")
print("v1.0.0 record count: {0}   v1.1.0 record count: {1}".format(len(traffic_res_data), len(new_traffic_data)))
print("")
print("--- Example data from v1.1.0 database ---")
for i in range(0,5):
    try:
        print(new_traffic_data[i])
    except IndexError:
        pass
print("")

print("")
print("################ sms_data #################")
print("v1.0.0 record count: {0}   v1.1.0 record count: {1}".format(len(sms_res_data), len(new_sms_data)))
print("")
print("--- Example data from v1.1.0 database ---")
for i in range(0,5):
    try:
        print(new_sms_data[i])
    except IndexError:
        pass
print("")