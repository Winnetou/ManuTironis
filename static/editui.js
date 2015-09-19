 $(document).ready(function(){
 	//make header sitcky
    $("#header").sticky({topSpacing:0});
    //zoom option on the page scan
    //disabled for now
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
			activate_save_button()
			//$('#approve_word').prop('disabled', false);
			
		} 
		else if ($('#correction_option').val() == "incorr")
			{
				deactivate_save_button()
				var incorr = $('#asitis').text()
				get_suggestions(incorr);			
			}
		else
		{
			deactivate_save_button()
			$('#corr_list').empty();
		}
		})

});
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
}

function set_to_default() //set all to default, called by click on word
{
	$('#corr_list').empty(); // first, clean the list
	deactivate_save_button()//next, disable save button
	//third, values of both dropdowns back to zero
	$('#correction_option').prop('disabled', false);
	$('#correction_option').val("init");
	$('#semantic_spec').prop('disabled', false);
	$('#semantic_spec').val("init");
	$('#asitis').prop('contenteditable',false);
	$('#asitis').css('color','inherit')
}
function disable() //called after saved button clicked
{
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
		})
}
function save()
{
	disable()
	var page_id = $("#page_id").val();
	var word_id = $("#word_id").val();
	var correct_form = $('#asitis').text();
	//now, send it all

	//if ok, change button to SAVED!
}