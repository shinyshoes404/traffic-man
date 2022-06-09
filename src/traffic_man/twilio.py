import os, base64, requests

class TwilioSender:
    def __init__(self):
        self.url = "https://api.twilio.com/2010-04-01/Accounts/" + os.environ.get("TWILIO_ACCOUNT_SID") + "/Messages.json"
        
        basic_auth = os.environ.get("TWILIO_ACCOUNT_SID") + ":" + os.environ.get("TWILIO_AUTH_TOKEN")
        basic_auth_bytes = basic_auth.encode("utf-8")
        base64_bytes = base64.b64encode(basic_auth_bytes)
        base64_auth = base64_bytes.decode("ascii")

        self.headers = {"Authorization": "Basic " + base64_auth, "Content-Type": "application/x-www-form-urlencoded"}
        self.from_phone = os.environ.get("FROM_NUM")
    
    def send_bad_traffic_sms(self, phone_nums: list):
        for num in phone_nums:
            req_body = {
                "Body": "Traffic is looking pretty bad",
                "To": num,
                "From": self.from_phone
            }


            resp = requests.post(url=self.url, headers=self.headers, data=req_body)
            print(req_body)
            print(resp.status_code)
            print(resp.content)
    
    def send_resolved_traffic_sms(self, phone_nums: list):
        for num in phone_nums:
            req_body = {
                "Body": "It looks like traffic has cleared up.",
                "To": num,
                "From": self.from_phone
            }
            resp = requests.post(url=self.url, headers=self.headers, data=req_body)
            print(req_body)
            print(resp.status_code)


