

from flashcards.misc import get_secrets
from google.cloud import firestore
from google.oauth2 import service_account


def get_db_connection():
    # Setup DB access
    secrets = get_secrets()
    db = firestore.Client(
        project=secrets["GOOGLE_PROJECT_ID"],
        credentials=service_account.Credentials.from_service_account_info(
            secrets["GOOGLE_SERVICE_ACCOUNT_SECRETS"]
        )
    )
    return db


db = get_db_connection()

db.collection("Documents").document("Tags").get(
    field_paths=["TEST", "KA_INTRO_BIO_03"]
).to_dict()













####################################
#
#
#
#              TESTING 
#
#
#
####################################
db = flashcards.get_db_connection()





x = db.collection('Scores').document("Biology")
x.get().to_dict()

############# Adding data
data = {"question": "a", "answer":"D" }
db.collection("Subjects").document("Biology").set(data)

############# Updating (merging) data
data1 = {"LOT1":  { "question": "abc", "answer" : "def", "score" : "B"} }
data2 = {"LOT1":  {"score" : "E"} }

# Will replace the fields
db.collection("Subjects").document("Biology").update(data1)
db.collection("Subjects").document("Biology").update(data2)

# Will replace just the listed field 
db.collection("Subjects").document("Biology").set(data1, merge=True)
db.collection("Subjects").document("Biology").set(data2, merge=True)


############# Get data
for i in db.collection("Subjects").stream():
    print(i.id)
    print(i.to_dict())

db.collection("Subjects").document("Biology").get().to_dict()


############# Deleting documents / fields
db.collection('Subjects').document('Biology').update({'LOT1': firestore.DELETE_FIELD})
db.collection('Subjects').document('Biology').delete()






############# Updating (merging) data
data1 = { "question": "abc", "answer" : "def", "score" : "B"} 
data2 =  {"score" : "E"} 

# Will replace the fields
db.collection("Subjects").document("Biology").collection("LOT1").update(data1)
db.collection("Subjects").document("Biology").collection("LOT1").update(data2)

# Will replace just the listed field 
db.collection("Subjects").document("Biology").collection("LOT1").set(data1, merge=True)
db.collection("Subjects").document("Biology").collection("LOT1").set(data2, merge=True)



db.collection("Subjects").document("Biology").get().to_dict().keys()


x = db.collection("Subjects").document("Biology")
y = x.get(field_paths= {"question"})
y.to_dict()

for i in x.collections():
    print(i)
    print(i.id)

 
class test(object):
    
    
    def __init__(self):
        
        
        if i == 1: 
            print("hello, world")




import flashcards.database as db

dbm = db.dbmanager()

dbm.fetch_col_item("Scores", "A+zqpbYJ4cZaRzRp", ["0EF9_34FO"])