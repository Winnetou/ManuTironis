 $(document).ready(function(){


    $("#join").click(function( ) {
        $('#action').val("join");
        disable()
        var word_id = $("#word_id").val();
        var selectorr = "#"+ word_id
        var the = $(selectorr)
        var hash_next_id = the.next()
        var next_word_text = $(hash_next_id).text();


        var concatenated;
        var half = $(this).attr('half');
        if (typeof half !== typeof undefined && half !== false && half=="2")
        {
            alert("gotcha")
            concatenated  = $('#word_id').text() + next_word_text;
        }
        else
            {
               concatenated  = $('#asitis').text() + next_word_text;
            }
        // todo - if
        strip_and_send_to_asitis(concatenated)
        $('#asitis').effect("highlight",  {color:"#FF8080"}, 3000);
        activate_save_button()
        change_save_btn("join")
        })

    $("#divide").click(function( ) {
        $('#action').val("divide");
        disable()
        activate_save_button()
        $('#asitis').attr('disabled', false);
        change_save_btn("divide")
        $('#asitis').effect("highlight",  {color:"#FF8080"}, 3000);
        $('#asitis').prop('contenteditable',true);
        $('#asitis').focus();
        // saving is done is main js script
        })

});


function change_save_btn(action)
{
    //change target of the SAVE button
    $('#approve_word').attr("target", action);

}

function join()
{
    disable()
    var word_id = $("#word_id").val();
    var word = $('#asitis').text();
    var data = {
        'word_id':word_id,
        'word': word
    }

    $.ajax({
        url: '/join',
        type: "POST",
        data: data,
        success: function(data){
            $(hash_word_id).replaceWith(data);
        }

    })
    reset_save_btn_to_default()
    return
}


function divide()
{
    disable()
    var word_id = $("#word_id").val();
    var word = $('#asitis').text();
    var hash_word_id = "#"+word_id;
    var data = {
    'word_id':word_id,
    'word': word
    }
    //now, send it all
    var url = '/divide'

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data){

            $(hash_word_id).replaceWith(data);
        }
    })

    reset_save_btn_to_default()
    return
}



function divideorjoin()
{
    disable()
    var action = $('#action').val();
    var page_id = $("#page_id").val();
    var word_id = $("#word_id").val();
    var word = $('#asitis').text();
    var data = { 'page_id':page_id,
    'word_id':word_id,
    'action': action,
    'word': word
    }
    //now, send it all
    var url = '/divideorjoin'

    $.ajax({
        url: url,
        type: "POST",
        data: data,

    })
    if (action=="join")
    {
        //take the word, change its text
        var hash_word_id = "#"+word_id;
        $(hash_word_id).text(word);
        var next_id = parseInt(word_id)+1;
        var hash_next_id = "#"+next_id;
        $(hash_next_id).hide();

    }
    if (action=="divide")
    {
        //take the word, change its text
        var hash_word_id = "#"+word_id;
        $(hash_word_id).text(word);
    }

    reset_save_btn_to_default()
    return
}

function reset_save_btn_to_default()
{
    //button SAVE was changed, reset it
    $('#approve_word').attr("target","update");
    $('#action').val("");

}
