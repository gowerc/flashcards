
# Database Structure

This document just outlines the basic database structure used in this project

```
Users:
    <UserHash>:
        Email:
        Created:
        TagSelection:
        TagSelectionDate:
        CanFlagQuestions:

Sessions:
    <SessionHash>:
        UserHash:
        Created:
        Expires:

Questions:
    <QuestionHash>:
        Question:
        Answer:
        Flagged:

Scores:
    <UserHash>:
        <QuestionHash>: <Score>

Documents:
    TagMeta:
        <TagID>:
            Name:
            Rank:
    Tags:
        <DocumentID> : [ <TagIDs> ]
    
    Questions:
        <DocumentID> : [ <QuestionHashes>]


```