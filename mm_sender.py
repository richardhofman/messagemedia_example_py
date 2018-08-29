import sys
import os
import datetime
import phonenumbers

import requests, json
import hashlib, hmac
import base64

def compute_hmac(payload_md5, date, http_req, api_secret):
    # Format the identity string, to be signed by API secret.
    compounded_str = "Date: %s\nContent-MD5: %s\n%s" % (date, payload_md5, http_req)

    # Generate signature with HMAC-SHA, and base64 encode the result.
    hmac_bytes = hmac.new(api_secret.encode("ascii"), msg=compounded_str.encode("ascii"), digestmod=hashlib.sha1).digest()
    hmac_sig = base64.b64encode(hmac_bytes).decode("utf-8")

    return hmac_sig

def generate_headers(payload, api_secret, api_key):
    # Generate hex digest (MD5) of payload string (as ASCII bytes).
    payload_md5 = hashlib.md5(payload.encode('ascii')).hexdigest()

    # Generate the RFC7231 HTTP-Date format string, and define HTTP request string.
    date_str = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
    http_req_str = "POST /v1/messages HTTP/1.1"

    # Compute HMAC
    hmac_sig = compute_hmac(payload_md5, date_str, http_req_str, api_secret)

    # Define Authorization header format string.
    authz_header = 'hmac username="%s", algorithm="hmac-sha1", headers="Date Content-MD5 request-line", signature="%s"'

    # Define the request headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Content-MD5': payload_md5,
        'Date': date_str,
        'Authorization': authz_header % (api_key, hmac_sig)
    }

    return headers

def send_sms(api_key, api_secret, dest_num, message):
    # Ensure we have a valid number, and format it in E.164
    number = phonenumbers.parse(dest_num, 'AU')
    if not phonenumbers.is_valid_number(number):
        print("%s is not a valid phone number." % str(dest_num))
        sys.exit(1)
    number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    # Prepare request payload
    api_data = {
        "messages": [
            {
                "content": message,
                "destination_number": number,
                "metadata": {
                    "github_info": "Message sent with https://github.com/richardhofman/messagemedia_example_py"
                }
            }
        ]
    }
    request_payload = json.dumps(api_data)

    headers = generate_headers(request_payload, api_secret, api_key)

    # Construct and send the request!
    resp = requests.post(url="https://api.messagemedia.com/v1/messages", headers=headers, data=request_payload.encode("ascii"))
    if resp.status_code < 300 and resp.status_code > 200:
        print("Success! Received from MessageMedia API:\n")
        results = json.loads(resp.text)
        for key, value in results["messages"][0].items():
            print("%s => %s" % (key, value))
        sys.exit(0)
    else:
        print("Uh-oh. Something went wrong. Here's what MessageMedia's API said:\n" + resp.text)
        sys.exit(1)

if __name__ == "__main__":
    # Fail if we don't have a dest number.
    if len(sys.argv) < 2:
        print ("Please provide at least a destination number")
        sys.exit(1)
    
    # Fail if we don't have auth data.
    missing_envvars = [v for v in ['MESSAGEMEDIA_APIKEY', 'MESSAGEMEDIA_APISECRET'] if v not in os.environ.keys()]
    if len(missing_envvars) > 0:
        print("Please define the following environment variables:")
        for envvar in missing_envvars:
            print("* " + envvar)
        sys.exit(1)

    # Grab data
    api_key = os.environ['MESSAGEMEDIA_APIKEY']
    api_secret = os.environ['MESSAGEMEDIA_APISECRET']
    destination_number = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else "https://bit.ly/2MzCQSp"

    send_sms(api_key, api_secret, destination_number, message)