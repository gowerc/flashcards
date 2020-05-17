from google.cloud import firestore
import support
import support.database as database
import os
import importlib



dbm = database.dbmanager()

data_folder = "./content/"


meta = database.ContentMeta( data_folder + "meta.yml")


### Read in all content

content = {}

for  root, dirs, files in os.walk(data_folder):
    for file in files:
        if file.endswith(".yml") and file != "meta.yml":
            temp_content = database.Content( root + "/" + file)
            meta.add(temp_content)
            for key, value in temp_content.content.items():
                content[key] = value


### Update database Content

existing_content = dbm.fetch_col_list("content")

for key, value in content.items():
    if key not in existing_content:
        dbm.write_col_item("content", key, value)


for key in existing_content:
    if key not in content.keys():
        dbm.delete_col_item("content", key)




### Update database ContentMeta

existing_topics = dbm.fetch_col_list("meta")
existing_topic_meta = { topic : dbm.fetch_col_item("meta", topic) for topic in existing_topics}

meta.merge(existing_topic_meta)  ## Merge in existing scores
meta.prune()                     ## Remove unused topics

content_meta  = meta.content_meta

for key, value in content_meta.items():
    dbm.write_col_item("meta", key, value)


for topic in existing_topics:
    if topic not in content_meta.keys():
        dbm.delete_col_item("meta", topic)


### Update database Structure

content_struc  = meta.content_structure
old_structure = dbm.fetch_col_list("structure")

for key, value in content_struc.items():
    dbm.write_col_item("structure", key, value)


for struc in old_structure:
    if struc not in content_struc.keys():
        dbm.delete_col_item("structure", struc)



