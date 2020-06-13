

function onSignIn(googleUser) {
    let token = googleUser.getAuthResponse().id_token;
    console.log(token);
    $("#token").val(token);
    $("#login-form").submit()
}
