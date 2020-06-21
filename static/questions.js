


let question_id = ""


$(document).ready(async function () {
    await new_question();
    $("#button-correct").click(update_score(true));
    $("#button-incorrect").click(update_score(false));
    $("#button-show").click(() => {
        $("#answer-div").show()
        $("#button-show-answer").hide()
    });
    $("#button-skip").click(async function () {
        $("#question-text").html("");
        await new_question();
    });
});



async function new_question() {
    let resp = await fetch("/get_question");
    let content = await resp.json();

    question_id = content["QUESTION_ID"];

    let question_text = "";
    let answer_text = "";

    content["QUESTION"].forEach(element => { question_text = question_text + `<p>${element}</p>` });
    content["ANSWER"].forEach(element => { answer_text = answer_text + `<p>${element}</p>` });

    $("#question-text").html(question_text);
    $("#answer-text").html(answer_text);

    if (content["FLAGGED"]) {
        $('#question-card').addClass('bg-danger').removeClass('bg-light');
        $("#button-flag").html("Unflag");
    } else {
        $('#question-card').addClass('bg-light').removeClass('bg-danger');
        $("#button-flag").html("Flag");
    }
}

function update_score(was_correct) {
    return async function () {
        $("#answer-div").hide();
        $("#question-text").html("");
        $("#button-show-answer").show();
        let resp = await fetch("/update_question_score", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "question_id": question_id, "result": was_correct })
        });
        await new_question();
    }
}
