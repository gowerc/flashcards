import flask
import support
from flask_api import status
from functools import wraps
from pprint import pprint
app = flask.Flask(__name__)
env_vars = support.get_env_vars() 
db = support.get_db_connection()










def triage(f):
    @wraps(f)
    def decfun(*args, **kwargs):
        if not has_session_token():
            return send_to_login()

        if not is_valid_session_token():
            return send_to_login()
        
        return f()
    return decfun
        


def login













###################################
#
#
#   OLD
#
#



def validate_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        body = flask.request.json
        token = body["token"]
        if not support.is_valid_user(token):
            return "UNAUTHORIZED", status.HTTP_401_UNAUTHORIZED
        return f()
    return decorated_function


def ensure_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        path = flask.request.path
        if path == "/login":
            path = "/"
        
        
        if flask.request.method == "GET":
            return serve_login(location = path)
        
        try:
            token = flask.request.form["token"]
        except ValueError:
            serve_login(location = path)
        
        if token == None or token == "":
            return serve_login(location = path)
        
        
        if not support.is_valid_user(token):
            return serve_login(location = path)
            
        return f(*args, **kwargs)
    return decorated_function




@app.route('/get_question', methods=['POST'])
@validate_request
def get_question():
    body = flask.request.json
    subject = body["subject"]
    scores = support.get_question_scores(subject, db)
    question_id = support.get_random_question_id(scores)
    question = support.get_question( question_id, subject, db)
    question["ID"] = question_id
    return flask.jsonify(question)


@app.route('/update_score', methods=['POST'])
@validate_request
def update_score():
    
    body = flask.request.json
    subject = body["subject"]
    question_id = body["question_id"]
    question_result = body["question_result"]
    
    assert question_result in [ True, False], "Question result not logical"
    
    existing_score = support.get_question_scores(subject, db)[question_id]
    new_score = support.update_tier( existing_score, question_result)
    support.set_question_tier(question_id, new_score, subject, db)
    
    return "done", status.HTTP_200_OK



@app.route('/is_valid_user', methods=['POST'])
def is_valid_user_api():
    body = flask.request.json
    token = body["token"]
    return flask.jsonify({ "is_valid_user": support.is_valid_user(token)})



@app.route("/login", methods=['POST', "GET"])
def serve_login(location = "/"):
    return flask.render_template(
        "login.html", 
        CLIENT_ID = env_vars["GOOGLE_AUTH_URL"], 
        LOCATION = location
    )


@app.route("/questions/<subject>", methods=['POST', "GET"])
@ensure_logged_in
def serve_questions(subject):
    
    return flask.render_template(
        "questions.html", 
        CLIENT_ID = env_vars["GOOGLE_AUTH_URL"], 
        SUBJECT = subject
    )


@app.route("/", methods=['POST', "GET"])
@ensure_logged_in
def serve_subject():
    
    subjects = support.get_subjects(db)
    
    colors = [
        "primary" , "secondary" , "success", #"light", 
        "danger", "warning", "info", "dark"
    ]
    
    subjects_meta = [
        { "subject" : j, "color" : colors[ i % len(colors)]}
        for i,j in enumerate(subjects)
    ]
    
    return flask.render_template(
        "subjects.html", 
        CLIENT_ID=env_vars["GOOGLE_AUTH_URL"],
        items = subjects_meta
    )











