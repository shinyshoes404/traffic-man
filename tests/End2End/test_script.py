from traffic_man.twilio.twilio import TwilioSignature
import requests, sys, sqlite3


# classes to reuse TwilioSignature to create test request signatures
class Form:
    def __init__(self, req_parameters: dict):
        self.req_parameters = req_parameters
    def to_dict(self):
        return self.req_parameters

class Body:
    def __init__(self, req_parameters: dict):
        self.form = Form(req_parameters)


# initial subscribe
req_parameters = {"MessageSid": "randomid", "From": "+15555555555", "To": "+17777777777", "Body": "start"}
body = Body(req_parameters)
headers = {}
ts = TwilioSignature(body, headers)
headers["X-Twilio-Signature"] = ts._create_signature()
headers["Content-Type"] = "application/json"
resp = requests.post(url="http://127.0.0.1:8003/inbound", json=req_parameters, headers=headers)
if resp.status_code != 200:
    print("failed intitial subscribe")
    sys.exit(1)


# send pass phrase
req_parameters = {"MessageSid": "randomid", "From": "+15555555555", "To": "+17777777777", "Body": "Test code"}
body = Body(req_parameters)
headers = {}
ts = TwilioSignature(body, headers)
headers["X-Twilio-Signature"] = ts._create_signature()
headers["Content-Type"] = "application/json"
resp = requests.post(url="http://127.0.0.1:8003/inbound", json=req_parameters, headers=headers)
if resp.status_code != 200:
    print("failed pass phrase")
    sys.exit(1)

# check the data in the db
conn = sqlite3.connect("/builds/mnt/traffic-man-etc/traffic_man.db")
cur = conn.cursor()

cur.execute("SELECT * FROM sms_data;")
sms_rows = cur.fetchall()

cur.execute("SELECT * FROM phone_numbers;")
phone_num_rows = cur.fetchall()


cur.close()
conn.close()

if len(sms_rows) != 4:
    sys.exit(1)

if len(phone_num_rows) != 1:
    sys.exit()

if phone_num_rows[0][3] != "needs setup" or phone_num_rows[0][4] != "auth":
    sys.exit(1)