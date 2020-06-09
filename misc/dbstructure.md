
# Database Structure

This document just outlines the basic database structure used in this project

```
Users:
    UserHash:
        Email:
        Created:
        LastAccessed:
        TagSelection:
        CanUpdateScores:

Sessions:
    SessionHash:
    UserHash:
    Created:
    Expires:

Documents:
    DocumentID:
        QuestionHash:
            Score:
            Flagged:

Questions:
    QuestionHash:
        Question:
        Answer:

Meta:
    Tags:
        TagID:
            Name:
            Rank:
    Documents:
        DocumentID: Tags

```