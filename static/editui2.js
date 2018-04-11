// problems: DIVIDE WORD doesnt create another token in the DOM
// we have to renumber id after remove/divide/join

 $(document).ready(function(){
    $("#header").sticky({topSpacing:0});//make header sticky
    set_to_default()
    var last_greek = $('.greek_text').last()
    $("<hr>").insertAfter(last_greek);


//thats wrong, whatever inside greek span is clicked, should trigger that function
$('span[lang="grc"]').click(function (event) {
    set_to_default()
    $(event.target).addClass("shining");
    var incorr;
    var full = $(this).attr('full');
    var half = $(this).attr('half');
    var elem_id = $(this).attr('id')
    // if it is not
    if (typeof full !== typeof undefined && full !== false) {
        incorr = full;

        //also make shining the second half of the word
        var next_token = get_next_token(elem_id);

        var next_id = next_token.attr('id');
        $("#"+next_id).addClass("shining");
    }
    // if the word clicked if half=2

    else if (typeof half !== typeof undefined && half !== false && $(this).attr('half')=="2")
    {

            var prev_token = get_prev_token(elem_id);
            var prev_id = prev_token.attr('id');

            $("#"+prev_id).addClass("shining");
            incorr = prev_token.attr('full');

    }
    //just normal word
    else
    {
        incorr = $(event.target).text();

    }

    strip_and_send_to_asitis(incorr);

    var incorr_id = $(event.target).attr('id');
    //start with sending the id of the clicked word to hidden id input
    $("#word_id").val(incorr_id);

    // here we want to say that this form was recognized as either correct ot incorrect
    //and as either a word, pagination, number or proper name
    if ($(event.target).attr("corr")=="1")
    {

        $('#incorr').attr('disabled', false);
    }
    else if ($(event.target).attr("corr")=="0")
    {
        $('#corr').attr('disabled', false);
        $('#show_sugg').attr('disabled', false);
        $('#join').attr('disabled', false);
        $('#divide').attr('disabled', false);
        $('#remove').attr('disabled', false);
    }

    if (is_first_or_last_in_line(incorr_id)) {
        //enable pagination button
        $('#pagination').attr('disabled', false);
    }

})


$('#corr').click( function()
    {
        setcorrect()

})

$('#incorr').click( function()
    {
        setincorrect()
})

$('#remove').click( function()
    {
        $('#approve_word').attr("target","remove");
        disable()
        activate_save_button()
        var word_id = $("#word_id").val();
        $("#"+word_id).addClass("dying");

})
$('#pagination').click( function()
    {

        setpagination()
    })

$('#show_sugg').click( function()
    {
        $('#corr').attr('disabled', true);
        $('#show_sugg').attr('disabled', true);
        $('#asitis').prop('contenteditable',false);
        deactivate_save_button()
        var incorr = $('#asitis').text()
        get_suggestions(incorr);
})

$('#approve_word').click(function(event)
    {
        var target = $(this).attr('target');
        if (target=="update")
        {
            $('#corr_list').empty();
            $('#asitis').prop('contenteditable',false);
            deactivate_save_button()
            $('#corr_list').empty();
            save();
            // id of the word clicked is word_id hidden field
            var incorr_id = "#"+$("#word_id").val();
            var text_of_correct = $('#asitis').text();
            // change the text
            $(incorr_id).text(text_of_correct);
            // change it to correct
            $(incorr_id).attr("corr","1");
        }
        if (target=="join")
        {
             join()
        }
        if (target=="divide")
        {
            divide()
        }
        if (target=="remove")
        {
            really_remove()
        }

})

});




function deactivate_save_button()
{
    $('#approve_word').attr('disabled', true);
    //then, change the color and make transition
}

function activate_save_button()
{
    $('#approve_word').attr('disabled', false);
    //then, change the color and make transition
}

function accept_suggestion(incorr)
{
    // send the text to asitis
    $('#asitis').text(incorr);
    // fade all other buttons magnify clicked
    activate_save_button()
    $('#capitalise').prop('disabled', false);
}

function capitalise()
{
    var capitalised = $('#asitis').text();
    capitalised = capitalised.substr(0,1).toUpperCase()+capitalised.substr(1);
    $('#asitis').text(capitalised);
}

function set_to_default() //set all to default, called by click on word
{
    $('#approve_word').attr("target","update")
    $('span').each(function() {
            $(this).removeClass("shining");
            $(this).removeClass("dying");
        })
    //$("#play_correct").text("Start");
    $('#corr_list').empty(); // first, clean the list
    deactivate_save_button()//next, disable save button
    //third, values of both dropdowns back to zero
    $('#corr').attr('disabled', true);
    $('#incorr').attr('disabled', true);
    $('#show_sugg').attr('disabled', true);
    $('#join').attr('disabled', true);
    $('#divide').attr('disabled', true);
    $('#remove').attr('disabled', true);
    $('#pagination').attr('disabled', true);
    $('#asitis').prop('contenteditable',false);
    $('#asitis').css('color','inherit');
    $('#alphabet').hide();
    $('.diacritics').each(function() {
            $(this).hide();
        })

}
function disable() //called after saved button clicked
{
    $('span').each(function() {
            $(this).removeClass("shining");
        })
    $('#corr_list').hide();
    $('#alphabet').hide();
    $('#corr_list').empty(); // first, clean the list
    deactivate_save_button() //next, disable save button
    $('#corr').attr('disabled', true);
    $('#incorr').attr('disabled', true);
    $('#show_sugg').attr('disabled', true);
    $('#join').attr('disabled', true);
    $('#divide').attr('disabled', true);
    $('#asitis').prop('contenteditable',false);
    $('#asitis').attr('disabled', true);
    $('#remove').attr('disabled', true);
    $('#pagination').attr('disabled', true);

}

function get_suggestions(word)
{
    var incorr = $('#asitis').text();
    var url = '/suggest'
    $.getJSON( url, {word:incorr}
        ).done(function(data){
            if (! $.isEmptyObject(data))
            {
                $.each(data, function(i, item)
                {
                    var p = '<li><button onclick=accept_suggestion("'+item+'") class="suggestion">'+item+'</button></li>';
                    $('#corr_list').append(p);
                });

            }
            else
            {
                var p = '<li>No suggestions found!</li>';
                $('#corr_list').append(p);
            }
            var capital = '<li><button id="capitalise" disabled="disabled" onclick=capitalise() class="suggestion">Capitalise</button></li>';
            $('#corr_list').append(capital);
            // CO ZA KICHA PONIZEJ ! ! ! ! ! ! FIXME - THAT KICHA CANNOT STAY
            var but = '<li><button onclick=make_editable() class="suggestion">Edit it manually</button></li>';
            $('#corr_list').append(but);
            $('#corr_list').show('slow')
        })
}
// func save is used when picked word
// from suggestions or hand-corrected
// and clicked on SAVE btn
function save()
    {
    disable()
    var word_id = $("#word_id").val();
    var correct_form = $('#asitis').text();
    //now, send it all
    var data1 = {
        'word_id':word_id,
        'correct_form':correct_form,
        }
    $.ajax({
        url: '/update',
        type: "POST",
        data: data1,
        success: function(data){

            $(hash_word_id).replaceWith(data);
        }

    })

}



function setpagination()
{
    var word_id = $("#word_id").val();
    var hash_word_id = '#'+word_id;
    disable()
    var data = {
        'word_id':word_id
        }
    var url = '/setpagination'

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data){

            $(hash_word_id).replaceWith(data);
        }

    })
    renumber_tokens()
}

function setincorrect()
{
    var pre_id = $("#word_id").val();
    var id = '#'+pre_id;
    disable()
    var word_id = $("#word_id").val();
    var data = {
        'word_id':word_id
        }
    var url = '/setincorrect'

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data){

            $(id).replaceWith(data);
        }

    })
    return
}
function setcorrect()
{
    var pre_id = $("#word_id").val();
    var id = '#'+pre_id;
    disable()
    var word_id = $("#word_id").val();
    var data = {
        'word_id':word_id
        }
    var url = '/setcorrect'

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data){

            $(id).replaceWith(data);
        }

    })
    return
}
/*
function old_mark_as(mark)
{
    disable()
    var page_id = $("#page_id").val();
    var word_id = $("#word_id").val();
    var data = { 'page_id':page_id,
    'word_id':word_id,
    'mark': mark
    }
    //now, send it all
    var url = '/mark'

    $.ajax({
        url: url,
        type: "POST",
        data: data,


    })
    return
}
*/
function really_remove()
{
    disable()
    $('#approve_word').attr("target","update");
    var word_id = $("#word_id").val();
    var data = {
        'word_id':word_id,
    }
    var id = '#'+word_id;

    //now, send it all
    var url = '/remove'

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data){

            $(id).replaceWith(data);
        }

    })
    renumber_tokens()
    return
}

function strip_and_send_to_asitis(incorr)
{

    var last = incorr.length - 1
    if (incorr.slice(last) == ".")
        {
            incorr = incorr.substring(0, last);
        };
    if (incorr.slice(last) == ",")
        {
            incorr = incorr.substring(0, last);
        };

    $('#asitis').text(incorr);
}


function get_prev_token(incorr_id){
    var elem_id = '#' + incorr_id;
    var element = $(elem_id);
    var ordinal = parseInt($(elem_id).attr('ordinal'));
    var next_one = ordinal-1;
    var selector = 'span[ordinal='+next_one.toString()+']';
    var prev_one = $(selector);
    return prev_one
}


function get_next_token(incorr_id){

    // returns id of the next token
    var elem_id = '#' + incorr_id;
    var element = $(elem_id);
    var ordinal = parseInt($(elem_id).attr('ordinal'));
    var next_one = ordinal+1;
    var selector = 'span[ordinal='+next_one.toString()+']';
    var next_one = $(selector);
    return next_one

}

function is_first_in_line(incorr_id){

    var elem_id = '#' + incorr_id;
    var element = $(elem_id);
    var line = element.parent()
    var first_in_line = line.children()[0]

    if (
        element.is(first_in_line)
        ){
            return true
        }
        else {
            return false

    };
}


function is_last_in_line(incorr_id){

    var elem_id = '#' + incorr_id;
    var element = $(elem_id);
    var line = element.parent()
    var last_in_line = line.children()[line.children().length - 1]

    if (element.is(last_in_line) ){
            return true
        }
    else {
            return false
    };
}

function is_first_or_last_in_line(incorr_id){

    if (
        is_last_in_line(incorr_id) || is_first_in_line(incorr_id)
    ){
        return true
    }
    else {
         return false
    };
}