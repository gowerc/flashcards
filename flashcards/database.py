from .logger import log
from .misc import get_secrets
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


class dbmanager(object):
    def __init__(self):
        self.db = get_db_connection()
        self.key = {
            "Users": "Users",
            "Sessions": "Sessions",
            "Questions": "Questions",
            "Documents": "Documents",
            "Scores": "Scores"
        }
    
    def fetch_col_list(self, col):
        dbname = self.key[col]
        log.info("Fetching list of items for %s ...", dbname)
        return [i.id for i in self.db.collection(dbname).list_documents()]
    
    def fetch_col_item(self, col, id, fields=None):
        dbname = self.key[col]
        log.info("Fetching item %s from %s ...", id, col)
        return self.db.collection(dbname).document(id).get(field_paths=fields).to_dict()
    
    def write_col_item(self, col, id, content):
        dbname = self.key[col]
        log.info("Writing item %s into %s ...", id, dbname)
        self.db.collection(dbname).document(id).set(content)
        return None
    
    def delete_col_item(self, col, id):
        dbname = self.key[col]
        log.info("Deleting item %s from %s ...", id, dbname)
        self.db.collection(dbname).document(id).delete()
        return None
    
    def update_col_item(self, col, id, content):
        dbname = self.key[col]
        log.info("Updating item %s into %s ...", id, dbname)
        self.db.collection(dbname).document(id).set(content, merge=True)
        return None
