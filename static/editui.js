 $(document).ready(function(){
    $("#header").sticky({topSpacing:0});//make header sitcky
    //zoom option on the page scan disabled for now
    //$("#scanpage").elevateZoom({ 
    //    zoomType    : "lens", 
    //    lensShape : "round", 
    //    lensSize : 300 
    //});  
 	$("<hr>").insertAfter($('.greek_text')); // draw a line to separate greek text from latin tranlsation

 	// iterate over very side_pagination
 	//if it's first child, give it class left
 	//if it's last child, give it class right


//thats wrong, whatever inside greek span is clicked, should trigger that function
$('span[lang="grc"]').click(function (event) {
	var incorr = $(event.target).text();
	$('#asitis').text(incorr);
	var incorr_id = $(event.target).attr('id');  
	//start with sending the id of the clicked word to hidden id input
	$("#word_id").val(incorr_id);
	set_to_default()
	// here we want to say that this form was recognized as either correct ot incorrect 
	//and as either a word, pagination, number or proper name
	if ($(event.target).attr("corr")=="1")
	{
		//to be implemented later
		//$('#approve_word').text("This is not correct");
	}
	else
	{
	}

	 

})
	$('#correction_option').change( function()
		{
		if ($('#correction_option').val() == "corr") //user says its correct
		{
			$('#corr_list').empty(); // first, clean the list
			$('#asitis').prop('contenteditable',false);
			$('#asitis').css('color','red');
			activate_save_button()
			//$('#approve_word').prop('disabled', false);
			
		} 
		else if ($('#correction_option').val() == "incorr")
			{
				$('#asitis').prop('contenteditable',false);
				deactivate_save_button()
				var incorr = $('#asitis').text()
				get_suggestions(incorr);			
			}
		else
		{
			$('#asitis').prop('contenteditable',false);
			deactivate_save_button()
			$('#corr_list').empty();
		}
		})
	//below - all functionality of the alphabet
	$('.vowel').click(function(event) //here we click on eg a+ button and show available diacritics 
	{
	var nam = "#"+$(event.target).attr('name');
	//alert(nam);
	//var newbtn = '<li><button>+</button></li>';
	$('.diacritics').hide();
	$(nam).show();
	})

	$('#asitis').focus(function(){ //when input active, show alphabet
		$('#alphabet').show();
	})
	
	// now - writing with virtual keyboard
	$('.grklt').click(function(event){
		var areaId = 'asitis';
		var text = $(event.target).text();
		insertAtCaret(areaId,text) 
	})


	

});
function shiftcases()
{

	if ($('#shift').attr('state')=='down')//( $('#alphabet').first().text() == $('#alphabet').first().text().toUpperCase() )
	{
		$('#shift').attr('state', 'up');
		$('.grklt').each( function(){
		$(this).text($(this).text().toUpperCase()); 
		}	)
	}
	else
	{
		$('#shift').attr('state', 'down');
		$('.grklt').each( function(){
		$(this).text($(this).text().toLowerCase()); 
		})
	}
}


function deactivate_save_button()
{
	$('#approve_word').prop('disabled', true);
	//then, change the color and make transition
}

function activate_save_button()
{
	$('#approve_word').prop('disabled', false);
	//then, change the color and make transition
}

function accept_suggestion(incorr)
{

	$('#asitis').text(incorr);
	//alert(incorr);
	activate_save_button()
	//$('#approve_word').prop('disabled', false);
}
function make_editable()
{
	$('#asitis').prop('contenteditable',true);
	$('#asitis').focus();
	$('#corr_list').hide('slow');
	$('#corr_list').empty(); // lastly, clean the list
	//$('#correction_option').hide('slow');
	$('#corr_list').hide('slow');
}

function set_to_default() //set all to default, called by click on word
{	
	//$('#corr_list').hide('slow');
	$('#corr_list').empty(); // first, clean the list
	deactivate_save_button()//next, disable save button
	//third, values of both dropdowns back to zero
	$('#correction_option').prop('disabled', false);
	$('#correction_option').val("init");
	$('#semantic_spec').prop('disabled', false);
	$('#semantic_spec').val("init");
	$('#asitis').prop('contenteditable',false);
	$('#asitis').css('color','inherit');
	$('#alphabet').hide('slow');
}
function disable() //called after saved button clicked
{
	$('#corr_list').hide('slow');
	$('#alphabet').hide('slow');
	$('#corr_list').empty(); // first, clean the list
	deactivate_save_button() //next, disable save button
	//third, values of both dropdowns back to zero
	$('#correction_option').prop('disabled', true);
	$('#correction_option').val("init");
	$('#semantic_spec').prop('disabled', true);
	$('#semantic_spec').val("init");
	$('#asitis').prop('contenteditable',false);
	$('#asitis').css('color','#CCCCCC');
	
}

function get_suggestions(word)
{
	var incorr = $('#asitis').text();
	var url = 'http://127.0.0.1:5000/suggest'
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
			var but = '<li><button onclick=make_editable() class="suggestion">Edit it manually</button></li>';
			$('#corr_list').append(but);
			$('#corr_list').show('slow')
		})
}
function save()
{
	disable()
	var word_id = $("#word_id").val();
	var correct_form = $('#asitis').text();
	//now, send it all
	var url1 = '/update'
	var data1 = {
	'word_id':word_id,
	'correct_form':correct_form
	}
	$.ajax({
		url: url1,
		type: "POST",
		data: data1,

	})
	//var posting = $.post( url,data);
	//if ok, change button to SAVED!
	//posting.done(function( data ) {
    //alert("JFHG")
  //});
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