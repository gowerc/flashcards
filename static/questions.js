function update_then_fetch(result){
    return function(){
        $("#answer-div").hide() ;
        $('#button-show-answer').show();
        update_score(result);
        fetch_new_question();
    }
}


function update_score(result){
    fetch('/update_score',{
        method: 'post',
        body: JSON.stringify( {
            "token" : flashcards_global["token"], 
            "question_result" : result,
            "question_id" : flashcards_global["question_id"],
            "subject": flashcards_global["subject"]
        }),
        headers: { 'Content-type': 'application/json' }
    })
    .then(
        function(response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +response.status);
                return;
            }
        }
    )
    .catch(function(err) {
        console.log('Fetch Error :-S', err);
    });
}


function fetch_new_question() {
    
    flashcards_global["question"].html("");
    flashcards_global["answer"].html("");
    
    fetch('/get_question',{
        method: 'post',
        body: JSON.stringify({
            "token" : flashcards_global["token"],
            "subject": flashcards_global["subject"]
        }),
        headers: { 'Content-type': 'application/json' }
    })
    .then(
        function(response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +response.status);
                return;
            }
            // Examine the text in the response
            response.json().then(function(data) {
                
                
                jQuery.each(data.question, function(i, val){
                    var newq = flashcards_global["question"].html() + "<p>" + val + "</p>";
                    flashcards_global["question"].html(newq);
                })
                
                jQuery.each(data.answer, function(i, val){
                    var newa = flashcards_global["answer"].html() + "<p>" + val + "</p>";
                    flashcards_global["answer"].html(newa);
                })
                
                flashcards_global["question_id"] = data.ID
            });
        }
    )
    .catch(function(err) {
        console.log('Fetch Error :-S', err);
    });
}


function google_ready(){
    fetch_new_question();
}



$( document ).ready(function() {
    
    flashcards_global["question"] = $("#question-text");
    flashcards_global["answer"] = $("#answer-text");
    flashcards_global["subject"] = JSON.parse($('#question-meta-data').attr('data-question'))["subject"];
    
    
    
    $( "#button-correct" ).click(update_then_fetch(true));
    $( "#button-incorrect").click(update_then_fetch(false));
    
    $( "#button-show" ).click(function(){
        $("#answer-div").show();
        $('#button-show-answer').hide();
    });
    
});