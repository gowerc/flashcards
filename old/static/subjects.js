




function google_ready(){
    $(".subject-link").each( function(index,value){
        var url;
        url = $(value).attr( "data-url" );
        $(value).click( function(){ post(url)});
    });
    
    $("#subject-content").show();
}




