
var flashcards_global = {
    "token" : "",
    "question_id" : "",
    "subject" : "",
    "question" : "",
    "answer" : ""
};

function onSignIn(googleUser) {
    $("#button-signin").hide();
    $("#button-signout").show();
    flashcards_global["token"] = googleUser.getAuthResponse().id_token;
    google_ready();
}

function google_ready(){}; 

$( document ).ready(function() {
    $( "#button-signout" ).on( "click", function(){
        var auth2 = gapi.auth2.getAuthInstance();
        auth2.signOut().then(function () {
            console.log('User signed out.');
            location.reload();
            window.location.href = "/login";
        });
    });
    
    $("#subjects-button").click(function() {post("/")});
    
});




function post(url){
    var form = $('<form action="' + url + '" method="post" style="display: none">' +
    '<input type="text" name="token" value="' + flashcards_global["token"] + '" />' +
    '</form>');
    $('body').append(form);
    form.submit();
}






