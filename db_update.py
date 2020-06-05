import os
import support.database as database
import support.contentManager as contentManager


dbm = database.dbmanager()

data_folder = "./content/"

tags = contentManager.Tags(data_folder + "tags.yml")

# Read in all content
documents = []
new_questions = {}
new_docids = []

for root, dirs, files in os.walk(data_folder):
    for file in files:
        if file.endswith(".yml") and file != "tags.yml":
            document = contentManager.Document(root + "/" + file)
            documents.append(document)
            tags.add_document(document)
            new_docids.append(document.docid)
            new_questions = {**new_questions, **document.content}


dbm.write_col_item("Meta", "Tags", tags.content)
dbm.write_col_item("Meta", "Documents", tags.documents)

# Update Questions
existing_questions = dbm.fetch_col_list("Questions")

for question_hash in new_questions.keys():
    if question_hash not in existing_questions:
        dbm.write_col_item("Questions", question_hash, new_questions[question_hash])


for question_hash in existing_questions:
    if question_hash not in new_questions.keys():
        dbm.delete_col_item("Questions", question_hash)


# Update Scores

# Extract a list of all existing scores and flatten it (so the dict keys are the question hashes)
# Update scores to keep the old scores
old_scores_collection_ids = dbm.fetch_col_list("Scores")
old_scores_collection = {docid: dbm.fetch_col_item("Scores", docid) for docid in old_scores_collection_ids}

old_scores = {}
for docid in old_scores_collection.keys():
    for question_hash in old_scores_collection[docid].keys():
        old_scores[question_hash] = old_scores_collection[docid][question_hash]

for document in documents:
    document.merge_scores(old_scores)

for document in documents:
    docid = document.docid
    if document.scores != old_scores_collection.get(docid):
        dbm.write_col_item("Scores", document.docid, document.scores)

for docid in old_scores_collection.keys():
    if docid not in new_docids:
        dbm.delete_col_item("Scores", docid)
