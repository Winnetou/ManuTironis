 $(document).ready(function(){

    $( "body" ).append('<ol style="display:none" id="XSS"></ol>');
    $('span[corr="0"]').each(function() {
        var the_id = $(this).attr('id');
        var pe = "<li>"+the_id+"</li>";
        $("#XSS").append(pe)
    })


    $("#play_correct" ).click(function() {
        // FIXME if #XSS has no children, change button to
        // finish and return
        set_to_default()
        disable()
        $("#play_correct" ).text("Skip >>");
        $('#asitis').attr('disabled', false);
        var the_one = $( "#XSS li:first-child" );
        var id_of_incorrect = the_one.text();
        //delete first child
        var id = "#"+id_of_incorrect;
        $(id).addClass("shining");
        var incorr = $(id).text();
        strip_and_send_to_asitis(incorr);
        //send the id of the clicked word to hidden id input
        $("#word_id").val(id_of_incorrect);
        $('#corr').attr('disabled', false);
        the_one.remove()

    })
/*
    $("#corr").click(function() {
        var pre_id = $("#word_id").val();
        var id = '#'+pre_id;
        $(id).removeClass("shining");
        $(id).attr("corr", "1");
        $("#play_correct" ).text("Next >>")
        // saving is done is main js script
        })
*/
});
