import re
import json
import hashlib
import yaml
from .logger import log


def read_yaml_file(fileloc):
    """
    Load yaml files but checking to make sure the top level keys are not duplicated
    """
    with open(fileloc, "r") as fi:
        pattern = re.compile("^[a-zA-Z]")  # Find all lines that don't start with white space
        text = fi.readlines()
        text2 = [i for i in text if pattern.findall(i)]
        text3 = [i.replace(" ", "").rstrip().replace(":", "") for i in text2]
        
        try:
            assert len(text3) == len(set(text3))
        except AssertionError as err:
            log.exception("Keys are not unique")
            raise err
            
    with open(fileloc, "r") as fi:
        dat = yaml.safe_load(fi)
    return dat


def keys_to_upper(dic):
    return {key.upper(): value for key, value in dic.items()}


class Document(object):
    def __init__(self, filename):
        self.filename = filename
        self.content_raw = read_yaml_file(filename)
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
        
        self.content = {
            question.question_hash: question.content for question in self.questions
        }
        
        self.scores = self.get_intial_scores()
        
    def validate_content(self):
        """
        Convert keys all to Upper case then ensure they conform to the expected standards
        """
        content_raw_upper = keys_to_upper(self.content_raw)
        
        tags = content_raw_upper.pop("TAGS")
        docid = content_raw_upper.pop("DOCID")
        
        self.assert_doc_meta(docid, tags)
        
        dic_ret = {"TAGS": [tag.upper() for tag in tags], "DOCID": docid}
        
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
    
    def get_intial_scores(self):
        scores = {}
        for question_hash in self.question_hashes:
            scores[question_hash] = {
                "SCORE": "E",
                "FLAGGED": False
            }
        return scores
    
    def merge_scores(self, oldscores):
        for question_hash in self.scores.keys():
            old_values = oldscores.get(question_hash)
            if old_values is not None:
                self.scores[question_hash] = old_values


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


class Tags(object):
    def __init__(self, filename):
        self.filename = filename
        self.content_raw = read_yaml_file(filename)
        self.content = self.validate_content()
        self.documents = {}
    
    def validate_content(self):
        content_raw_upper = keys_to_upper(self.content_raw)
        content = {}
        for tagid in content_raw_upper.keys():
            tagmeta = {}
            tagmeta_raw = keys_to_upper(content_raw_upper[tagid])
            name = tagmeta_raw["NAME"]
            rank = tagmeta_raw["RANK"]
            self.assert_tag_meta(name, rank, tagid)
            tagmeta["NAME"] = name
            tagmeta["RANK"] = rank
            content[tagid] = tagmeta
        return content
    
    def assert_tag_meta(self, name, rank, tagid):
        try:
            assert isinstance(name, str)
        except AssertionError as e:
            log.exception("Tag name is not character \n%s\n%s", self.filename, tagid)
            raise e
            
        try:
            assert isinstance(rank, int)
        except AssertionError as e:
            log.exception("Tag rank is not numeric\n%s\n%s", self.filename, tagid)
            raise e
    
    def add_document(self, document):
        try:
            assert isinstance(document, Document)
        except AssertionError as e:
            log.exception("Object is not a document")
            raise e
        
        docid = document.docid
        tags = document.tags
        
        if docid in self.documents.keys():
            log.exception("Duplicate document id detected: %s", docid)
            raise KeyError()
        
        allowed_tags = self.content.keys()
        
        for tag in tags:
            if tag not in allowed_tags:
                log.exception("Unknown tag used in document: %s\n%s", docid, tag)
                raise KeyError()
        
        self.documents[docid] = tags
