////////////////////////////////////////////////////////////////////////////////
//  ENTER CONFIGURATION INFO. HERE                                            //
////////////////////////////////////////////////////////////////////////////////

//  Enter the relative web path to the cgi-bin with a trailing / (probably "/cgi-bin/")
var cgibinPath = "/cgi-bin/";



////////////////////////////////////////////////////////////////////////////////
//  END CONFIGURATION INFO. ENTRY                                             //
//  BEGIN FUNCTIONALITY FOR GENERAL SET-UP                                    //
////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
	// when the document is loaded, do some preparatory stuff.

	// make sure the first element after the legend of each fieldset has the "firstEltAfterLegend" class
	// (this just affects the display a little bit, nicer looking spacing)
	$('legend').next().addClass('firstEltAfterLegend');

	// bind to the submit action on the main form so that we submit with ajaxSubmit
	// instead of a traditional POST to the web server.
	$('#mainForm').ajaxForm({url: cgibinPath + 'preProcessForm.cgi',
		dataType: 'xml',
		success: mainFormSubmitSucceeded,
		error: mainFormSubmitFailed});

	// create a hidden form to be used when we are ready to go to the results page.
	$(document.createElement("form")).attr('id', 'formGoToResults')
					//info for submitting the form
					.attr('method', 'POST')
					.attr('action', cgibinPath + 'displayResults.cgi')
					.attr('enctype', 'multipart/form-data')
					.append($(':input[name="RScriptToCall"]').clone())
					.appendTo($('#hidden'));
});



////////////////////////////////////////////////////////////////////////////////
//  END FUNCTIONALITY FOR GENERAL SET-UP                                      //
//  BEGIN FUNCTIONALITY FOR GETTING A SESSION ID                              //
////////////////////////////////////////////////////////////////////////////////

function mainFormSubmitSucceeded(responseXML, statusText, xhr, $form) {
// This function is called upon successful completion of an AJAX call to preprocess the form

	if($(responseXML).find('status').text() == "success") {
		var sessionID = Number($(responseXML).find('sessionID').text());

		//remove old session ID field, if applicable
		$(':input[name="sessionID"]').remove();

		//add new hidden field with session id to the main form
		var sessionField = $(document.createElement('input')).attr('type', 'hidden')
			.attr('name', 'sessionID')
			.val(sessionID);

		$('#formGoToResults').append(sessionField);

		$('#formGoToResults').submit();
	} else {
	    mainFormSubmitFailed(responseXML, statusText, xhr, $form);
	}
}

function mainFormSubmitFailed(responseXML, statusText, xhr, $form) {
// This function is called upon failed completion of an AJAX call to get the session ID
// Called if the AJAX call fails outright or from get SessionIDSucceeded if the status was other than 'success'

	if($(responseXML).find('status').text() == "error") {
		alert($(responseXML).find('message').text());
	} else {
		alert('There was an error in processing your submission.  Please try again.  If you continue to get an error, please contact the web site maintainers.' + statusText);
	}
}
