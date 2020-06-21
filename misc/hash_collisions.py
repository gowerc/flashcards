

slots = 60.0 ** 8.0
items = 100000
placed = 0.0

prob_of_no_collision = 1.0

for i in range(1, items + 1):
    prob_of_no_collision = prob_of_no_collision * ((slots - placed) / slots)
    placed = placed + 1

(1 - prob_of_no_collision) * 100


# Storage space consumption

question_name_size = 10.0
questions_per_document = 10.0
document_name_size = 30.0

question_size = question_name_size + 1 + ((document_name_size + 1) / questions_per_document)

1000000 / question_size

1000000 / 15
