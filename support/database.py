import support
from .logger import log


class dbmanager(object):
    def __init__(self):
        self.db = support.get_db_connection()
        self.key = {
            "Users": "Users",
            "Sessions": "Sessions",
            "Questions": "Questions",
            "Documents": "Documents",
            "Meta": "Meta"
        }
    
    def fetch_col_list(self, col):
        dbname = self.key[col]
        log.info("Fetching list of items for %s ...", dbname)
        return [i.id for i in self.db.collection(dbname).list_documents()]
    
    def fetch_col_item(self, col, id):
        dbname = self.key[col]
        log.info("Fetching item %s from %s ...", id, col)
        return self.db.collection(dbname).document(id).get().to_dict()
    
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
