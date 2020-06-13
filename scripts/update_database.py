import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import flashcards.database as database
import flashcards.contentManager as contentManager


dbm = database.dbmanager()

data_folder = "./content/"

# Read in all content
document_store = contentManager.DocumentStore(data_folder + "tags.yml")
question_store = contentManager.QuestionStore()

for root, dirs, files in os.walk(data_folder):
    for file in files:
        if file.endswith(".yml") and file != "tags.yml":
            document = contentManager.Document(root + "/" + file)
            document_store.add_document(document)
            question_store.add_document(document)


# Update Tags

dbm.write_col_item("Documents", "TagMeta", document_store.meta_data)
dbm.write_col_item("Documents", "Questions", document_store.questions)
dbm.write_col_item("Documents", "Tags", document_store.tags)

# Update Questions

existing_questions = dbm.fetch_col_list("Questions")

for question_hash in question_store.content.keys():
    if question_hash not in existing_questions:
        dbm.write_col_item("Questions", question_hash, question_store.content[question_hash])


for question_hash in existing_questions:
    if question_hash not in question_store.content.keys():
        dbm.delete_col_item("Questions", question_hash)


# Update Scores

scores = contentManager.Scores(list(question_store.content.keys()))

existing_users_list = dbm.fetch_col_list("Scores")
existing_users_scores = {}

# Ensure "default" user always exists
if "Default" not in existing_users_list:
    existing_users_list.append("Default")
    dbm.write_col_item("Scores", "Default", scores.default_scores)


for user in existing_users_list:
    existing_users_scores[user] = dbm.fetch_col_item("Scores", user)
    scores.add_user(user)
    scores.merge_user_scores(user, existing_users_scores[user])

for user in existing_users_list:
    if scores.content[user] != existing_users_scores[user]:
        dbm.write_col_item("Scores", user, scores.content[user])
