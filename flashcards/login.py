import base64
import flask
import datetime
import hashlib
import argon2
import json
import random
from .database import dbmanager
from .misc import get_secrets, get_now
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


def get_google_info(token):
    idinfo = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        get_secrets()["GOOGLE_AUTH_URL"]
    )
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        return False, {}
    if not idinfo["email_verified"]:
        return False, {}
    return True, idinfo


def get_session_token():
    token = flask.request.cookies.get('session')
    return token


def is_session_token_valid(token):
    dbm = dbmanager()
    session_list = dbm.fetch_col_list("Sessions")
    if token not in session_list:
        return False
    
    session = dbm.fetch_col_item("Sessions", token)
    
    if session["Expires"] < get_now():
        return False
    
    return True


def get_user_hash(user_email):
    size = 16
    hash_bytes = hashlib.blake2b(user_email.encode("utf-8"), digest_size=size * 3).digest()
    hash_ascii = base64.b64encode(hash_bytes).decode("utf-8")[:size]
    return hash_ascii


def create_session_hash(google_info):
    hasher = argon2.PasswordHasher(
        time_cost=6,
        memory_cost=102400,
        parallelism=1,
        hash_len=16,
        salt_len=16,
    )
    content = json.dumps(google_info, sort_keys=True).encode("utf-8")
    hash_bytes = hasher.hash(content)
    hash_ascii = base64.b64encode(hash_bytes.encode("utf-8")).decode("utf-8")
    return hash_ascii.replace("/", "_").replace("+", "_")


def create_new_session(google_info):
    dbm = dbmanager()
    user_hash = get_user_hash(google_info["email"])
    
    create_user_if_not_exist(google_info)
    
    user = dbm.fetch_col_item("Users", user_hash)
    
    if not user["CanUseApp"]:
        return None
        
    created = get_now()
    expires = created + datetime.timedelta(days=3, seconds=random.random() * 20)
    
    google_info["app_session_create"] = str(created)
    google_info["app_session_expires"] = str(expires)
    google_info["app_salt"] = get_secrets()["SALT"]
    session_hash = create_session_hash(google_info)
    
    session_info = {
        "UserHash": user_hash,
        "Created": created,
        "Expires": expires
    }
    dbm.write_col_item("Sessions", session_hash, session_info)
    return session_hash, expires


def create_user_if_not_exist(google_info):
    dbm = dbmanager()
    user_email = google_info["email"]
    user_hash = get_user_hash(user_email)
    user_has_list = dbm.fetch_col_list("Users")
    if user_hash in user_has_list:
        return
    
    user = {
        "Email": user_email,
        "Created": get_now(),
        "TagSelection": [],
        "TagSelectionDate": None,
        "CanFlagQuestions": False,
        "CanUseApp": True
    }
    
    default_scores = dbm.fetch_col_item("Scores", "Default")
    dbm.write_col_item("Users", user_hash, user)
    dbm.write_col_item("Scores", user_hash, default_scores)


class ActiverUser(object):
    def __init__(self):
        self.dbm = dbmanager()
        self.session_hash = get_session_token()
        self.session_list = self.dbm.fetch_col_list("Sessions")
        
        if self.session_hash not in self.session_list:
            self.has_valid_session = False
            return
            
        self.session_info = self.dbm.fetch_col_item("Sessions", self.session_hash)
        
        if self.session_info["Expires"] < get_now():
            self.has_valid_session = False
            self.dbm.delete_col_item("Sessions", self.session_hash)
        else:
            self.has_valid_session = True
    
    def get_user_info(self):
        self.user_info = self.dbm.fetch_col_item("Users", self.session_info["UserHash"])
        self.user_hash = self.session_info["UserHash"]
        self.tag_selection = self.user_info["TagSelection"]
        self.can_flag = self.user_info["CanFlagQuestions"]
        if self.tag_selection is None:
            self.tag_selection = []
