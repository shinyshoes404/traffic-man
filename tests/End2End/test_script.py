import os, base64, requests, hashlib, hmac, sys, sqlite3
from time import sleep


class TwilioSignature:
    def __init__(self, request_body, headers: dict):
        self.request_body = request_body
        self.headers = headers
   
    def _create_param_str(self) -> str:
        req_body_dict = self.request_body.form.to_dict()
        keys = list(req_body_dict.keys())
        keys.sort()
        param_str = ""
        for key in keys:
            param_str = param_str + key + req_body_dict.get(key)
        
        return param_str
    
    def _create_signature(self) -> str:
        key = bytes(os.environ.get("TWILIO_AUTH_TOKEN"), "UTF-8")
        contents = bytes(os.environ.get("TWILIO_WEBHOOK_URL") + self._create_param_str(), "UTF-8")
        hmac_obj = hmac.new(key, contents, hashlib.sha1)
        signature = hmac_obj.digest()
        # encode hmac signature to base64, then decode bytes to be a utf-8 string
        signature_base64_str = base64.b64encode(signature).decode('UTF-8')

        return signature_base64_str



# classes to reuse TwilioSignature to create test request signatures
class Form:
    def __init__(self, req_parameters: dict):
        self.req_parameters = req_parameters
    def to_dict(self):
        return self.req_parameters

class Body:
    def __init__(self, req_parameters: dict):
        self.form = Form(req_parameters)

print("running test script")
# initial subscribe
print("initial subscribe")
req_parameters = {"MessageSid": "randomid", "From": "+15555555555", "To": "+17777777777", "Body": "start"}
body = Body(req_parameters)
headers = {}
ts = TwilioSignature(body, headers)
headers["X-Twilio-Signature"] = ts._create_signature()
# headers["Content-Type"] = "application/x-www-form-urlencoded"
resp = requests.post(url="http://docker:8003/inbound", data=req_parameters, headers=headers)
if resp.status_code != 200:
    print("failed intitial subscribe")
    print(resp.status_code)
    print(resp.content)
    print(os.environ.get("TWILIO_AUTH_TOKEN"))
    print(os.environ.get("TWILIO_WEBHOOK_URL"))
    print(ts._create_param_str())
    print(ts._create_signature())
    with open("/builds/mnt/traffic-man-etc/traffic-man.log", "r") as log:
        print(log.read())
    sys.exit(1)


# send pass phrase
print("send pass phrase")
req_parameters = {"MessageSid": "randomid", "From": "+15555555555", "To": "+17777777777", "Body": "Test code"}
body = Body(req_parameters)
headers = {}
ts = TwilioSignature(body, headers)
headers["X-Twilio-Signature"] = ts._create_signature()
# headers["Content-Type"] = "application/x-www-form-urlencoded"
resp = requests.post(url="http://docker:8003/inbound", data=req_parameters, headers=headers)
if resp.status_code != 200:
    print("failed pass phrase")
    print(resp.status_code)
    print(resp.content)
    print(os.environ.get("TWILIO_AUTH_TOKEN"))
    print(os.environ.get("TWILIO_WEBHOOK_URL"))
    print(ts._create_param_str())
    print(ts._create_signature())
    with open("/builds/mnt/traffic-man-etc/traffic-man.log", "r") as log:
        print(log.read())
    sys.exit(1)

sleep(3)
print("starting database checks")
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
    print("failed sms data length")
    print(len(sms_rows))
    print(sms_rows)
    print("------------- traffic-man.og --------------")
    with open("/builds/mnt/traffic-man-etc/traffic-man.log", "r") as log:
        print(log.read())
    sys.exit(1)

if len(phone_num_rows) != 1:
    print("failed phone num lenth")
    print(len(phone_num_rows))
    print(phone_num_rows)
    print("------------- traffic-man.og --------------")
    with open("/builds/mnt/traffic-man-etc/traffic-man.log", "r") as log:
        print(log.read())
    sys.exit()

if phone_num_rows[0][3] != "needs setup" or phone_num_rows[0][4] != "auth":
    print("failed user validation")
    print(phone_num_rows)
    print("------------- traffic-man.og --------------")
    with open("/builds/mnt/traffic-man-etc/traffic-man.log", "r") as log:
        print(log.read())
    sys.exit(1)

print("tests passed")