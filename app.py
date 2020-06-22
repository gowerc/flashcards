import json
import flask
import flashcards.login as login
import flashcards.misc as misc
import flashcards.database as database
import flashcards.questions as questions
from functools import wraps
app = flask.Flask(__name__)

secrets = misc.get_secrets()


def session_redirect(page, redirect_if="valid"):
    def fun(f):
        @wraps(f)
        def triage(*args, **kwargs):
            
            assert redirect_if in ["valid", "invalid"]
            
            active = login.ActiverUser()
            
            valid = active.has_valid_session
            
            if redirect_if == "invalid":
                valid = not valid
            
            if valid:
                return flask.redirect(flask.url_for(page))
            return f(*args, **kwargs)
        return triage
    return fun


def api_ensure_valid_session(f):
    @wraps(f)
    def triage(*args, **kwargs):
        active = login.ActiverUser()
        if not active.has_valid_session:
            return "", 401
        return f(active)
    return triage


@app.route('/error')
def page_error(code):
    flask.abort(code)


@app.route("/session", methods=["POST"])
@session_redirect("index", redirect_if="valid")
def page_sessions():
    
    google_token = flask.request.form.get("token")
    if google_token is None:
        return page_error(401)
    
    is_valid_token, google_info = login.get_google_info(google_token)
    
    if not is_valid_token:
        return page_error(401)
    
    session_hash, session_expires = login.create_new_session(google_info)
    
    response = flask.make_response(flask.render_template("session.html"))
    response.set_cookie("session", session_hash, expires=session_expires)
    
    return response


@app.route("/login")
@session_redirect("page_index", redirect_if="valid")
def page_user_login():
    return flask.render_template(
        "login.html",
        CLIENT_ID=secrets["GOOGLE_AUTH_URL"]
    )


@app.route("/")
@session_redirect("page_user_login", redirect_if="invalid")
def page_index():
    return flask.render_template("questions.html")


color_map = {
    "1": "#33ce4a",
    "2": "#82dd4d",
    "3": "#cbea4d",
    "4": "#f2c960",
    "5": "#f47f3f"
}


@app.route("/selection")
@session_redirect("page_user_login", redirect_if="invalid")
def page_selection():
    dbm = database.dbmanager()
    tag_meta = dbm.fetch_col_item("Documents", "TagMeta")
    tagids = list(tag_meta.keys())
    tagids.sort()
    tag_meta_list = [
        {
            "tagid": tagid,
            "name": tag_meta[tagid]["NAME"],
            "colour": color_map[str(tag_meta[tagid]["RANK"])]
        }
        for tagid in tagids
    ]
    return flask.render_template(
        "selection.html",
        TAGS=tag_meta_list
    )


@app.route("/get_selection", methods=["GET"])
@api_ensure_valid_session
def get_selection(active):
    active.get_user_info()
    tag_selection = active.tag_selection
    return flask.Response(
        json.dumps(tag_selection),
        status=200,
        mimetype='application/json'
    )


@app.route("/set_selection", methods=["POST"])
@api_ensure_valid_session
def set_selection(active):
    active.get_user_info()
    new_selection = flask.request.get_json()["selection"]
    assert isinstance(new_selection, list)
    tag_meta = active.dbm.fetch_col_item("Documents", "TagMeta")
    for tag in new_selection:
        if tag not in tag_meta.keys():
            return "", 400
    
    update_user = {"TagSelection": new_selection}
    active.dbm.update_col_item("Users", active.user_hash, update_user)
    return "", 200


@app.route("/get_tagcombinations", methods=["GET"])
@api_ensure_valid_session
def get_tagcombinations(active):
    tags = active.dbm.fetch_col_item("Documents", "Tags")
    return flask.Response(
        json.dumps(tags),
        status=200,
        mimetype='application/json'
    )


@app.route("/get_tagmeta", methods=["GET"])
@api_ensure_valid_session
def get_tagmeta(active):
    tagmeta = active.dbm.fetch_col_item("Documents", "TagMeta")
    return flask.Response(
        json.dumps(tagmeta),
        status=200,
        mimetype='application/json'
    )


@app.route("/get_question", methods=["GET"])
@api_ensure_valid_session
def get_question(active):
    active.get_user_info()
    tag_selection = active.tag_selection
    document_tags = active.dbm.fetch_col_item("Documents", "Tags")
    selected_document_ids = [
        key
        for key, value in document_tags.items()
        if questions.contains_tags(value, tag_selection)
    ]
    document_questions = active.dbm.fetch_col_item("Documents", "Questions", selected_document_ids)
    possible_questions = [item for qlist in document_questions.values() for item in qlist]
    possible_question_scores = active.dbm.fetch_col_item(
        "Scores",
        active.user_hash,
        possible_questions
    )
    selected_question_id = questions.select_question_id(possible_question_scores)
    selected_question = active.dbm.fetch_col_item("Questions", selected_question_id)
    selected_question["QUESTION_ID"] = selected_question_id
    return flask.Response(
        json.dumps(selected_question),
        status=200,
        mimetype='application/json'
    )


@app.route("/update_question_score", methods=["POST"])
@api_ensure_valid_session
def update_question_score(active):
    active.get_user_info()
    data = flask.request.get_json()
    question_id = data["question_id"]
    result = data["result"]
    assert isinstance(result, bool)
    assert isinstance(question_id, str)
    user_hash = active.user_hash
    existing_score = active.dbm.fetch_col_item("Scores", user_hash, [question_id])[question_id]
    new_score = questions.update_score(existing_score, result)
    active.dbm.update_col_item("Scores", user_hash, {question_id: new_score})
    return "", 200


@app.route("/set_flag", methods=["POST"])
@api_ensure_valid_session
def set_flag(active):
    active.get_user_info()
    if not active.can_flag:
        return "", 401
    data = flask.request.get_json()
    question_id = data["question_id"]
    flagged = data["flagged"]
    assert isinstance(flagged, bool)
    assert isinstance(question_id, str)
    active.dbm.update_col_item("Questions", question_id, {"FLAGGED": flagged})
    return "", 200


@app.route("/get_canflag", methods=["GET"])
@api_ensure_valid_session
def get_canflag(active):
    active.get_user_info()
    return flask.Response(
        json.dumps({"CanFlag": active.can_flag}),
        status=200,
        mimetype='application/json'
    )
