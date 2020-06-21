import numpy as np

MAP_SCORE = {
    "A": 10,
    "B": 25,
    "C": 40,
    "D": 55,
    "E": 70,
    "F": 85
}

MAP_UPDATE_SCORE = {
    "A": "A",
    "B": "A",
    "C": "B",
    "D": "C",
    "E": "D",
    "F": "E"
}


def select_question_id(possible_question_scores):
    assert isinstance(possible_question_scores, dict)
    question_ids = list(possible_question_scores.keys())
    question_values = possible_question_scores.values()
    scores = [MAP_SCORE[i] for i in question_values]
    scores_np = np.array(scores)
    scores_np_probs = scores_np / scores_np.sum()
    selected_id = np.random.choice(question_ids, 1, replace=False, p=scores_np_probs)
    return selected_id[0]


def contains_tags(doc_tags, selected_tags):
    assert isinstance(doc_tags, list)
    assert isinstance(selected_tags, list)
    if selected_tags == []:
        return True
    return all(map(lambda x: x in doc_tags, selected_tags))


def update_score(score, was_correct):
    assert isinstance(was_correct, bool)
    if not was_correct:
        return "F"
    return MAP_UPDATE_SCORE[score]
