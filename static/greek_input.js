 $(document).ready(function(){
// all that come with greek input
//
//below - all functionality of the alphabet
    $('.vowel').click(function(event) //here we click on eg a+ button and show available diacritics
    {
    var nam = "#"+$(event.target).attr('name');
    //var newbtn = '<li><button>+</button></li>';
    $('.diacritics').hide();
    $(nam).show();
    })


    // now - writing with virtual keyboard
    $('.grklt').click(function(event){
        var areaId = 'asitis';
        var text = $(event.target).text();
        insertAtCaret(areaId,text)
    })

});

function make_editable()
{
    $('#corr').attr('disabled', true);
    $('#show_sugg').attr('disabled', true);
    $('#asitis').prop('contenteditable',true);
    $('#asitis').focus();
    $('#alphabet').show();
    $('#corr_list').hide();
    $('#corr_list').empty(); // lastly, clean the list
    $('#corr_list').hide();
    $('#approve_word').attr('disabled', false);
}

//copy&paste from http://stackoverflow.com/questions/1064089/inserting-a-text-where-cursor-is-using-javascript-jquery
function insertAtCaret(areaId,text) {
    var txtarea = document.getElementById(areaId);
    var scrollPos = txtarea.scrollTop;
    var strPos = 0;
    var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ?
        "ff" : (document.selection ? "ie" : false ) );
    if (br == "ie") {
        txtarea.focus();
        var range = document.selection.createRange();
        range.moveStart ('character', -txtarea.value.length);
        strPos = range.text.length;
    }
    else if (br == "ff") strPos = txtarea.selectionStart;

    var front = (txtarea.textContent).substring(0,strPos);
    var back = (txtarea.textContent).substring(strPos,txtarea.textContent.length);
    txtarea.textContent=front+text+back;
    strPos = strPos + text.length;
    if (br == "ie") {
        txtarea.focus();
        var range = document.selection.createRange();
        range.moveStart ('character', -txtarea.textContent.length);
        range.moveStart ('character', strPos);
        range.moveEnd ('character', 0);
        range.select();
    }
    else if (br == "ff") {
        txtarea.selectionStart = strPos;
        txtarea.selectionEnd = strPos;
        txtarea.focus();
    }
    txtarea.scrollTop = scrollPos;
}


function shiftcases()
{

    if ($('#shift').attr('state')=='down')//( $('#alphabet').first().text() == $('#alphabet').first().text().toUpperCase() )
    {
        $('#shift').attr('state', 'up');
        $('.grklt').each( function(){
        $(this).text($(this).text().toUpperCase());
        }   )
    }
    else
    {
        $('#shift').attr('state', 'down');
        $('.grklt').each( function(){
        $(this).text($(this).text().toLowerCase());
        })
    }
}
