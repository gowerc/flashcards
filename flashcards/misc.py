import json
import base64
import os
import datetime
import pytz


def get_secrets():
    secrets = json.loads(base64.b64decode(os.getenv("SECRETS")))
    secrets = {
        "GOOGLE_AUTH_URL": secrets["GOOGLE_AUTH_URL"],
        "GOOGLE_PROJECT_ID": secrets["GOOGLE_PROJECT_ID"],
        "GOOGLE_SERVICE_ACCOUNT_SECRETS": secrets["GOOGLE_SERVICE_ACCOUNT_SECRETS"],
        "GOOGLE_SERVICE_ACCOUNT": secrets["GOOGLE_SERVICE_ACCOUNT"],
        "GOOGLE_REGION": secrets["GOOGLE_REGION"],
        "GOOGLE_IMAGE": secrets["GOOGLE_IMAGE"],
        "SALT": secrets["SALT"]
    }
    
    for k, v in secrets.items():
        assert v is not None, "Environment variable {} is missing".format(k)
    
    return secrets


def get_now():
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    return now
