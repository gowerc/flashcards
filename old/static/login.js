



function google_ready(){
    
    fetch('/is_valid_user',{
        method: 'post',
        body: JSON.stringify( {"token" : flashcards_global["token"]}),
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
                if(data.is_valid_user){
                    
                    $("#token").val(flashcards_global["token"]);
                    $("#login-form").submit();
                    
                } else {
                    
                    $("#card-please-sign-in").hide();
                    $("#card-unauthorised").show();
                }
            });
        }
    )
    .catch(function(err) {
        console.log('Fetch Error :-S', err);
    });
    
    
}; 


