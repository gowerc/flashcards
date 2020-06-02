import re
import json
import hashlib
import yaml
import support


from .logger import log


class Document(object):
    def __init__(self, filename):
        self.filename = filename
        self.content_raw = self.read_yaml_file()
        self.content_validated = self.validate_content()
        self.docid = self.content_validated.pop("DOCID")
        self.tags = self.content_validated.pop("TAGS")
        
        self.questions = [
            Question(
                question=self.content_validated[QID].get("QUESTION"),
                answer=self.content_validated[QID].get("ANSWER")
            )
            for QID in self.content_validated.keys()
        ]
        
        self.question_hashes = [question.question_hash for question in self.questions]
        
    def read_yaml_file(self):
        """
        Load yaml files but checking to make sure keys aren't duplicated
        """
        with open(self.filename, "r") as fi:
            pattern = re.compile("^[a-zA-Z]")  # Find all lines that don't start with white space
            text = fi.readlines()
            text2 = [i for i in text if pattern.findall(i)]
            text3 = [i.replace(" ", "").rstrip().replace(":", "") for i in text2]
            
            try:
                assert len(text3) == len(set(text3))
            except AssertionError as err:
                log.exception("Keys are not unique")
                raise err
                
        with open(self.filename, "r") as fi:
            dat = yaml.safe_load(fi)
        return dat
        
    def validate_content(self):
        """
        Convert keys all to Upper case then ensure they conform to the expected standards
        """
        content_raw = self.content_raw
        content_raw_upper = {key.upper(): value for key, value in content_raw.items()}
        tags = content_raw_upper.pop("TAGS")
        docid = content_raw_upper.pop("DOCID")
        self.assert_doc_meta(docid, tags)
        dic_ret = {"TAGS": tags, "DOCID": docid}
        for question_id, question_cont in content_raw_upper.items():
            temp = {component.upper(): component_value for component, component_value in question_cont.items()}
            question = temp.get("QUESTION")
            answer = temp.get("ANSWER")
            self.assert_question_meta(question, answer, question_id)
            dic_ret[question_id] = {"QUESTION": question, "ANSWER": answer}
        return dic_ret
        
    def assert_doc_meta(self, docid, tags):
        try:
            assert isinstance(tags, list)
        except AssertionError as e:
            log.exception("Document Tags are not a list in: \n%s", self.filename)
            raise e
            
        try:
            assert isinstance(docid, str)
        except AssertionError as e:
            log.exception("Document ID is not a string in: \n%s", self.filename)
            raise e
        
    def assert_question_meta(self, question, answer, qid):
        try:
            assert isinstance(question, list) and isinstance(answer, list)
        except AssertionError as err:
            log.exception("Question/answer is not a list in: \n%s \nQID=%s", self.filename, qid)
            raise err


class Question(object):
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.content = self.get_content()
        self.question_hash = self.get_question_hash()
    
    def get_content(self):
        cur = {
            "QUESTION": self.question,
            "ANSWER": self.answer
        }
        return cur
    
    def get_question_hash(self):
        question_hash = hashlib.md5(
            json.dumps(
                self.content,
                sort_keys=True
            ).encode("utf-8")
        ).hexdigest()
        return question_hash





#####################
#
# TODO
#
#####################











class ContentMeta(object):
    """
    ## ContentStructure
    Bio :
        name: Biology
        topics : {
            bio01 : {
                name: Introduction to ....
                topic-hash: adawdaw
            }
    
    ## ContentMeta
    Topic-Hash
        Question-Hash : {
            Score
            Flagged
        }
        Question-Hash : {
            Score
            Flagged
        }
    """
    def __init__(self, filename):
        self.content_meta = {}
        self.content_structure = {}
        self.init_content_structure(filename)
        self.init_content_meta()
        
    def init_content_structure(self, filename):
        self.filename = filename
        self.content_structure_raw = self.read_yaml()
        content_structure = {}
        for subject_id, subject_value in self.content_structure_raw.items():
            subject_name = subject_value["NAME"]
            content_structure[subject_id] = {"NAME": subject_name, "TOPICS": {}}
            for topic_id, topic_name in subject_value["TOPICS"].items():
                topic_hash = hashlib.md5("{}-{}".format(subject_id, topic_id).encode("utf-8")).hexdigest()
                content_structure[subject_id]["TOPICS"][topic_id] = {"NAME": topic_name, "TOPIC_HASH": topic_hash}
        self.content_structure = content_structure
        
    def init_content_meta(self):
        content_meta = {}
        for subject_obj in self.content_structure.values():
            for topic_obj in subject_obj["TOPICS"].values():
                content_meta[topic_obj["TOPIC_HASH"]] = {}
        self.content_meta = content_meta
    
    def read_yaml(self):
        with open(self.filename, "r") as fi:
            dat = yaml.safe_load(fi)
        # TODO - Structure assertion checks
        return dat
    
    def get_topic_hash(self, subject, topic, error_hint=""):
        
        try:
            assert subject in self.content_structure.keys()
        except AssertionError as err:
            log.exception("Subject %s is not in the ContentStructure metadata\n%s", subject, error_hint)
            raise err
        
        subject_obj = self.content_structure[subject]
        
        try:
            assert topic in subject_obj["TOPICS"].keys()
        except AssertionError as err:
            log.exception("Topic %s is not in the subject %s ContentStructure metadata\n%s", topic, subject, error_hint)
            raise err
        return subject_obj["TOPICS"][topic]["TOPIC_HASH"]
        
    def add(self, content):
        
        try:
            assert isinstance(content, Content)
        except AssertionError as err:
            log.exception("Input should be a Content object")
            raise err
        
        subject = content.subject
        topic = content.topic
        filename = content.filename
        error_hint = "See file {}".format(filename)
        topic_hash = self.get_topic_hash(subject, topic, error_hint)
        for question_hash in content.hashes:
            self.content_meta[topic_hash][question_hash] = {
                "score": "D",
                "flagged": "N"
            }
            
    def merge(self, content_meta):
        
        try:
            assert isinstance(content_meta, dict)
        except AssertionError as err:
            log.exception("Input should be a dict object")
            raise err
         
        old_content = content_meta
        new_content = self.content_meta
        if old_content == {}:
            return None
        for topic_hash in new_content.keys():
            if topic_hash not in old_content.keys():
                continue
            for question_hash in new_content[topic_hash].keys():
                if question_hash not in old_content[topic_hash].keys():
                    continue
                new_content[topic_hash][question_hash] = old_content[topic_hash][question_hash]
        self.content_meta = new_content
    
    def topic_hash_lookup(self, topic_hash):
        content_structure = self.content_structure
        topic_name = ""
        for subject_obj in content_structure.values():
            for topic_id, topic_obj in subject_obj["TOPICS"].items():
                if topic_obj["TOPIC_HASH"] == topic_hash:
                    topic_name = topic_id
        return topic_name
    
    def prune(self):
        
        content_meta = self.content_meta
        empty_topic_hashes = [key for key, value in content_meta.items() if value == {}]
        new_content_meta = {key: value for key, value in content_meta.items() if value != {}}
        
        for topic_hash in empty_topic_hashes:
            log.warning("Pruning empty topic: %s", self.topic_hash_lookup(topic_hash))
        
        self.content_meta = new_content_meta
        
        new_content_structure = self.content_structure
        for subject_id, subject_value in new_content_structure.items():
            
            new_content_structure[subject_id]["TOPICS"] = {
                key: value
                for key, value in subject_value["TOPICS"].items()
                if value["TOPIC_HASH"] not in empty_topic_hashes
            }
        
        empty_subject_ids = [key for key, value in new_content_structure.items() if value["TOPICS"] == {}]
        
        for subject_id in empty_subject_ids:
            log.warning("Removing empty subject: %s", subject_id)
        
        new_content_structure = {key: value for key, value in new_content_structure.items() if value["TOPICS"] != {}}
        self.content_structure = new_content_structure


class dbmanager(object):
    
    def __init__(self):
        self.db = support.get_db_connection()
        self.key = {
            "content": "Content",
            "meta": "ContentMeta",
            "structure": "ContentStructure"
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
