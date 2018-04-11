 $(document).ready(function(){
    // when document ready, add numbers to tokens
    renumber_tokens();

});


function renumber_tokens(){
    // only greek tokens
    var ord = 1;
    var all_tokens = $("[corr]");
    $("span[corr]").each(function(){
        $(this).attr('ordinal', ord)
        ord++;
    })

};