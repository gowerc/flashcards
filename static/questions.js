


let question_id = ""


$(document).ready(async function () {
    $("#button-correct").click(() => new_question(true));
    $("#button-incorrect").click(() => new_question(false));
    $("#button-skip").click(() => new_question(null));
    $("#button-flag").click(() => set_flag(flagged = null, update_server = true));
    $("#button-show").click(() => {
        $("#answer-div").show()
        $("#button-show-answer").hide()
    });
    
    setup_flag_button()
    new_question(null);
});


async function new_question(was_correct = null) {
    
    update_score(was_correct, question_id)
    $("#answer-div").hide();
    $("#button-show-answer").hide();
    $("#question-text").html("");
    $("#answer-text").html("");
    
    set_flag(flagged = false, update_server = false)

    let resp = await fetch("/get_question");
    let content = await resp.json();

    question_id = content["QUESTION_ID"];

    let question_text = "";
    content["QUESTION"].forEach(element => { question_text = question_text + `<p>${element}</p>` });
    let answer_text = "";
    content["ANSWER"].forEach(element => { answer_text = answer_text + `<p>${element}</p>` });

    $("#question-text").html(question_text);
    $("#answer-text").html(answer_text);
    MathJax.typeset()

    set_flag(flagged = content["FLAGGED"], update_server = false)
    $("#button-show-answer").show()
}


async function update_score(was_correct, question_id) {
    if (was_correct === null) {
        return
    } else {
        await fetch("/update_question_score", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "question_id": question_id, "result": was_correct })
        });
    }
}


async function set_flag(flagged = null, update_server = false) {
    
    if (flagged === null) {
        if ($("#button-flag").text() === "Flag") {
            flagged = true
        } else {
            flagged = false
        }
    }
    
    if (flagged) {
        $('#question-card').removeClass('bg-light').addClass('bg-warning');
        $("#button-flag").html("Unflag");
    } else {
        $('#question-card').removeClass('bg-warning').addClass('bg-light');
        $("#button-flag").html("Flag");
    }

    if (update_server) {
        await fetch("/set_flag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "question_id": question_id, "flagged": flagged })
        });
    }
}


async function setup_flag_button() {
    resp = await fetch("/get_canflag")
    content = await resp.json()
    if (!content["CanFlag"]) {
        $("#button-flag").hide()
    }
}


