

function onSignIn(googleUser) {
    let token = googleUser.getAuthResponse().id_token;
    $("#token").val(token);
    $("#login-form").submit()
}
