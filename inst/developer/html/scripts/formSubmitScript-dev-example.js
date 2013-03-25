////////////////////////////////////////////////////////////////////////////////
//  ENTER CONFIGURATION INFO HERE                                             //
////////////////////////////////////////////////////////////////////////////////

//  Enter the relative web path to the cgi-bin with a trailing / (probably "/cgi-bin/")
var cgibinPath = "/cgi-bin/";

//  Enter the relative web path to the images directory with a trailing / (probably "/images/")
var imagesPath = "/images/";

////////////////////////////////////////////////////////////////////////////////
//  END CONFIGURATION INFO ENTRY                                              //
////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
	// when the document is loaded, do some preparatory stuff.

	// bind to the submit action on the file submit form so that we submit with ajaxSubmit
	// instead of a traditional POST to the web server.
	$('#fileSubmitForm').ajaxForm({url: cgibinPath + 'WebDevelopR-dev.cgi',
		dataType: 'xml',
		success: fileSubmitFormSucceeded,
		error: fileSubmitFormFailed});

	// bind to the submit action on the options submit form so that we submit with ajaxSubmit
	// instead of a traditional POST to the web server.
	$('#optionsSubmitForm').ajaxForm({url: cgibinPath + 'WebDevelopR-dev.cgi',
		dataType: 'xml',
		success: optionsSubmitFormSucceeded,
		error: optionsSubmitFormFailed});
});

function submitFile() {
	$('#fileSubmitForm').submit();
	appendLoading();
}

function submitToPlot() {
	$('#optionsSubmitForm').submit();
	appendLoading();
}

function appendLoading() {
	// Remove any content that is currently in the #plotContainer div.
	// This could be a plot from a previous data file.
	$('#plotContainer').children()
		.remove();

	// Create a text element that says "Loading..." and append it to the #plotContainer div.
	$('<h2>Loading...</h2>')
		.appendTo('#plotContainer');
}

function fileSubmitFormSucceeded(responseXML, statusText, xhr, $form) {
// This function is called upon successful completion of an AJAX call to submit the file selection form

	// Remove any content that is currently in the #plotContainer div.
	// This could be text that says "Loading..."
	$('#plotContainer').children()
		.remove();

	// Enable the "Plot!" button for submission of the #optionsSubmitForm
	$('#btnSubmitForm').removeAttr('disabled');

	// Add a new hidden field to the #optionsSubmitForm that contains
	// the session ID that was used for the submission of the fileSubmitForm.
	// We first remove any left over fields with session IDs from previous file uploads.
	$(':input[name="firstSessionID"]').remove();
	var sessionID = Number($(responseXML).find('sessionID').text());
	var sessionField = $('<input type="hidden" name="firstSessionID" />')
		.val(sessionID);
	$('#optionsSubmitForm').append(sessionField);

	// Parse the variable names in the uploaded data file.
	// These were returned in the XML output of the first R script.
	// They will be used as the options for the select boxes to choose
	// what variables to use for the x and y axes of the plot.
	var options = '';
	var i = 1;
	var varName = $(responseXML).find('var' + String(i)).text();
	while(varName) {
		options += '<option value="'+varName+'" class="added">'+varName+'</option>'
		i++;
		varName = $(responseXML).find('var' + String(i)).text();
	}	

	// Remove any options for variables to use in the plot that are left over
	// from previously uploaded data files.
	// Then add the new options from this data file.
	$('select').children().remove();
	$('select').append(options);
}

function fileSubmitFormFailed(responseXML, statusText, xhr, $form) {
// This function is called upon failed completion of an AJAX call to get the session ID
// Called if the AJAX call fails outright or from get SessionIDSucceeded if the status was other than 'success'
	alert('There was an error in processing your submission.  Please try again.  If you continue to get an error, please contact the web site maintainers.');
}

function optionsSubmitFormSucceeded(responseXML, statusText, xhr, $form) {
// This function is called upon successful completion of an AJAX call to submit the file selection form

	// Remove any content that is currently in the #plotContainer div.
	$('#plotContainer').children()
		.remove();

	// Add the image tag for the plot to the #plotContaienr div.
	// This tag was returned in the XML from the R script.
	$('#plotContainer').append($(responseXML).find('imgTagContainer').xml());
}

function optionsSubmitFormFailed(responseXML, statusText, xhr, $form) {
// This function is called upon failed completion of an AJAX call to create the plot.

	alert('There was an error in processing your submission.  Please try again.  If you continue to get an error, please contact the web site maintainers.');
}

function resetForm() {
	$(':input[name="firstSessionID"]').remove();
	$('.added').remove();
	$(':input[type = "file"]')
		.val("")
		.removeAttr('disabled');
	$(':input[type="radio"]').removeAttr('checked');
	$('#btnSubmitForm').attr('disabled','disabled');
	$('#plotContainer').children()
		.remove();
}
