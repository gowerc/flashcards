import flask
import flashcards.login as login
import flashcards.misc as misc
#from flask_api import status
from functools import wraps
app = flask.Flask(__name__)

secrets = misc.get_secrets()


def ensure_session(f):
    @wraps(f)
    def triage(*args, **kwargs):
        token = login.get_session_token()
        if token is None:
            return flask.redirect(flask.url_for('user_login'))

        if not login.is_session_token_valid(token):
            return flask.redirect(flask.url_for('user_login'))
        
        return f()
    return triage


@app.route('/error')
def error(code):
    flask.abort(code)


@app.route("/session", methods=["POST"])
def sessions():
    
    google_token = flask.request.form["token"]
    
    is_valid_token, google_info = login.get_google_info(google_token)
    
    if not is_valid_token:
        return error(401)
    
    session_hash, session_expires = login.create_new_session(google_info)
    
    response = flask.make_response(flask.render_template("session.html"))
    response.set_cookie("session", session_hash, expires=session_expires)
    
    return response


@app.route("/login")
def user_login():
    return flask.render_template(
        "login.html",
        CLIENT_ID=secrets["GOOGLE_AUTH_URL"]
    )


@app.route("/")
@ensure_session
def index():
    return "hello, world"


@app.route("/selection")
@ensure_session
def selection():
    pass







###################################
#
#
#   OLD
#
#



# def validate_request(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         body = flask.request.json
#         token = body["token"]
#         if not flashcards.is_valid_user(token):
#             return "UNAUTHORIZED", status.HTTP_401_UNAUTHORIZED
#         return f()
#     return decorated_function


# def ensure_logged_in(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
        
#         path = flask.request.path
#         if path == "/login":
#             path = "/"
        
        
#         if flask.request.method == "GET":
#             return serve_login(location = path)
        
#         try:
#             token = flask.request.form["token"]
#         except ValueError:
#             serve_login(location = path)
        
#         if token == None or token == "":
#             return serve_login(location = path)
        
        
#         if not flashcards.is_valid_user(token):
#             return serve_login(location = path)
            
#         return f(*args, **kwargs)
#     return decorated_function




# @app.route('/get_question', methods=['POST'])
# @validate_request
# def get_question():
#     body = flask.request.json
#     subject = body["subject"]
#     scores = flashcards.get_question_scores(subject, db)
#     question_id = flashcards.get_random_question_id(scores)
#     question = flashcards.get_question( question_id, subject, db)
#     question["ID"] = question_id
#     return flask.jsonify(question)


# @app.route('/update_score', methods=['POST'])
# @validate_request
# def update_score():
    
#     body = flask.request.json
#     subject = body["subject"]
#     question_id = body["question_id"]
#     question_result = body["question_result"]
    
#     assert question_result in [ True, False], "Question result not logical"
    
#     existing_score = flashcards.get_question_scores(subject, db)[question_id]
#     new_score = flashcards.update_tier( existing_score, question_result)
#     flashcards.set_question_tier(question_id, new_score, subject, db)
    
#     return "done", status.HTTP_200_OK



# @app.route('/is_valid_user', methods=['POST'])
# def is_valid_user_api():
#     body = flask.request.json
#     token = body["token"]
#     return flask.jsonify({ "is_valid_user": flashcards.is_valid_user(token)})



# @app.route("/login", methods=['POST', "GET"])
# def serve_login(location = "/"):
#     return flask.render_template(
#         "login.html", 
#         CLIENT_ID = env_vars["GOOGLE_AUTH_URL"], 
#         LOCATION = location
#     )


# @app.route("/questions/<subject>", methods=['POST', "GET"])
# @ensure_logged_in
# def serve_questions(subject):
    
#     return flask.render_template(
#         "questions.html", 
#         CLIENT_ID = env_vars["GOOGLE_AUTH_URL"], 
#         SUBJECT = subject
#     )


# @app.route("/", methods=['POST', "GET"])
# @ensure_logged_in
# def serve_subject():
    
#     subjects = flashcards.get_subjects(db)
    
#     colors = [
#         "primary" , "secondary" , "success", #"light", 
#         "danger", "warning", "info", "dark"
#     ]
    
#     subjects_meta = [
#         { "subject" : j, "color" : colors[ i % len(colors)]}
#         for i,j in enumerate(subjects)
#     ]
    
#     return flask.render_template(
#         "subjects.html", 
#         CLIENT_ID=env_vars["GOOGLE_AUTH_URL"],
#         items = subjects_meta
#     )











