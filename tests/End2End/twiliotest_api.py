import os, base64
from flask import Flask, request, make_response

twiliotest_api = Flask(__name__)

@twiliotest_api.route("/" + os.environ.get("TWILIO_ACCOUNT_SID") + "/Messages.json", methods=["POST"])
def send_sms():
    req_headers = request.headers
    if not req_headers.get("Authorization"):
        res = make_response("missing authorization header", 401)
        return res
    
    base64_bytes = req_headers.get("Authorization")[6:].encode("ascii")
    basic_auth_bytes = base64.b64decode(base64_bytes)
    basic_auth = basic_auth_bytes.decode("ascii")

    if basic_auth != os.environ.get("TWILIO_ACCOUNT_SID") + ":" + os.environ.get("TWILIO_AUTH_TOKEN"):
        res = make_response("incorrect authorization", 403)
        return res

    body = request.get_json()
    
    if not body.get("Body") or not body.get("To") or not body.get("From"):
        res = make_response("bad request", 400)
        return res
    
    res = make_response("", 201)
    return res

if __name__ == "__main__":
    twiliotest_api.run(host="0.0.0.0")