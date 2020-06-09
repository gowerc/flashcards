import os
import base64
import json
import numpy as np

from google.cloud import firestore
from google.oauth2 import service_account
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


def is_valid_user(token):
    
    env_vars = get_env_vars()
    
    idinfo = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        env_vars["GOOGLE_AUTH_URL"]
    )
    
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        return False
    
    if  not (idinfo['email'] == env_vars["GOOGLE_EMAIL"] and idinfo["email_verified"] == True):
        return False
    
    return True


def get_env_vars():
    secrets = json.loads(base64.b64decode(os.getenv("SECRETS")))
    env_vars = {
        "GOOGLE_AUTH_URL": secrets["GOOGLE_AUTH_URL"],
        "GOOGLE_PROJECT_ID": secrets["GOOGLE_PROJECT_ID"],
        "GOOGLE_SERVICE_ACCOUNT_SECRETS": secrets["GOOGLE_SERVICE_ACCOUNT_SECRETS"],
        "GOOGLE_SERVICE_ACCOUNT": secrets["GOOGLE_SERVICE_ACCOUNT"],
        "GOOGLE_REGION": secrets["GOOGLE_REGION"],
        "GOOGLE_IMAGE": secrets["GOOGLE_IMAGE"],
        "SALT": secrets["SALT"]
    }
    
    for k, v in env_vars.items():
        assert v is not None, "Environment variable {} is missing".format(k)
    
    return env_vars




TIER_PROBABILITIES = {
    "A" :  10,
    "B" :  25,
    "C" :  50,
    "D" : 100
}



def get_random_question_id(question_tiers, tierprob=TIER_PROBABILITIES):
    question_id = [k for k, v in question_tiers.items()]
    question_weights = [tierprob[v] for k, v in question_tiers.items()]
    question_weights_np = np.array(question_weights)
    probs = question_weights_np / question_weights_np.sum()
    
    question_chosen = np.random.choice(question_id, 1 , replace = False, p = probs)
    
    return question_chosen[0]





def update_tier(current, got_right):
    assert current in ["A", "B", "C", "D"], "Invalid input"
    if not got_right:
        return "D"
    return_obj = {
        "A" : "A",
        "B" : "A",
        "C" : "B",
        "D" : "C"
    }
    return return_obj[current]





def set_question_tier(question_id, tier, subject, db):
    assert tier in TIER_PROBABILITIES.keys(), "Invalid Tier"
    existing_scores = get_question_scores(subject, db)
    assert question_id in existing_scores.keys(), "Question ID {} does not exist in the scores DB for {}".format(question_id, subject)
    db.collection('Scores').document(subject).set({question_id: tier}, merge=True)
    return True




def get_question_scores(subject, db):
    a = db.collection('Scores').document(subject).get().to_dict()
    return a




def get_question(id,subject, db):
    a = db.collection(subject).document(id).get().to_dict()
    return a




def get_subjects(db):
    subs = db.collection("Scores").list_documents()
    return [ i.id for i in subs]