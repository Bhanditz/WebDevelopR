////////////////////////////////////////////////////////////////////////////////
//  ENTER CONFIGURATION INFORMATION HERE				      //

// Enter the number of seconds to wait between checks for status updates.
// e.g., statusUpdateFrequency = 5 means we will check for a new status
// every 5 seconds.
var statusCheckFrequency = 5;

// Enter the relative web path to the images folder on your web server
// (probably "/images/")
var imagesDir = "/images/";

//  END CONFIGURATION SECTION                                                 //
////////////////////////////////////////////////////////////////////////////////





////////////////////////////////////////////////////////////////////////////////
//  THE REAL SCRIPT BEGINS HERE						      //
////////////////////////////////////////////////////////////////////////////////

var statusCheckTimeoutID = 0;
//id number of the timeout used to check for updates on status

var mainFormSubmitCompleted = 0;
//indicates whether the main form submit has completed


////////////////////////////////////////////////////////////////////////////////
//  BEGIN FUNCTIONALITY FOR MISC PAGE AND FORM SET-UP                         //

$(document).ready(function() {
	//when the document is loaded, do some preparatory stuff.

	// Bind to the submit action on the CallR form
	// so that it submits via ajaxSubmit instead of a regular post to the web server.
	// Then submit the form.
	$('#formCallR').ajaxForm({dataType: 'xml',
		success: callRSucceeded,
		error: callRFailed})
		.submit();

	// Bind to the submit action on the CheckStatus form
	// so that it submits via ajaxSubmit instead of a regular post to the web server.
	$('#formCheckStatus').ajaxForm({dataType: 'xml',
		success: statusCheckSucceeded,
		error: statusCheckFailed,
		timeout: (10*1000)});

	// Start the process of checking for status updates.
	statusCheckTimeoutID = setTimeout("$('#formCheckStatus').submit()", statusCheckFrequency*1000);
});



////////////////////////////////////////////////////////////////////////////////
//  END FUNCTIONALITY FOR MISC PAGE AND FORM SET-UP                           //
//  BEGIN FUNCTIONALITY FOR HANDLING THE RESPONSE FROM THE MAIN FORM          //
////////////////////////////////////////////////////////////////////////////////

function callRSucceeded(responseXML, statusText, xhr, $form) {
// This function is called upon successful completion of an AJAX call to R

    if(!$.isXMLDoc(responseXML)) { alert("Script did not return a valid XML document:\n" + $(responseXML).xml()); }

	if($(responseXML).find('status').xml(1) == "" || $(responseXML).find('contents').xml() == "") {
		callRFailed(responseXML, statusText, xhr, $form);
	} else {
		mainFormSubmitCompleted = 1;
		clearTimeout(statusCheckTimeoutID);

		$('#statusloadingimg').fadeOut(function() {
			$('#statusImgContainer').append('<img src="' + imagesDir + 'filler.jpg" id="statusfillerimg" />');
			$(this).remove();
		});

       		updateStatusDisplay($(responseXML).find('status').xml(1));

		$('#contents').append($('<div id="resultsContainer" class="level1"> <p class="sectionHeader">Results:</p> <div id="displayResults"> </div> </div>').hide());
		$('#displayResults').html($(responseXML).find('contents').xml());
		$('#resultsContainer').slideDown();
	}
}

function callRFailed(responseXML, statusText, xhr, $form) {
// This function is called upon failed completion of an AJAX call to R

	mainFormSubmitCompleted = 1;
	clearTimeout(statusCheckTimeoutID);

	$('#statusloadingimg').fadeOut(function() {
		$('#statusImgContainer').append('<img src="' + imagesDir + 'filler.jpg" id="statusfillerimg" />');
		$(this).remove();
	});

	$('#contents').append($('<div id="resultsContainer" class="level1"> <p class="sectionHeader">Results:</p> <div id="displayResults"> There was an error either with the web server or your internet connection.  Please try again.  If you continue to encounter this problem, please contact the website hosts. </div> </div>').hide());
	$('#resultsContainer').slideDown();
}



////////////////////////////////////////////////////////////////////////////////
//  END FUNCTIONALITY FOR HANDLING THE RESPONSE FROM THE MAIN FORM            //
//  BEGIN FUNCTIONALITY FOR STATUS UPDATES                                    //
////////////////////////////////////////////////////////////////////////////////

function statusCheckSucceeded(responseXML, statusText, xhr, $form) {
// This function is called upon successful completion of an AJAX call checking status

	// We only need to do something if the main form has not finished processing yet.
	if(mainFormSubmitCompleted == 0) {

		if($(responseXML).find('status').xml(1) == "") {
			// If there isn't a status tag in the xml, something went wrong; put up an error message
			statusCheckFailed(responseXML, statusText, xhr, $form);
		} else {
			// If there is a status tag in the xml, display the status to the site user.
			$('#statusfillerimg').fadeOut(function() {
				$('#statusImgContainer').append('<img src="' + imagesDir + 'loadinfo.gif" id="statusloadingimg" />');
				$(this).remove();
			});

			updateStatusDisplay($(responseXML).find('status').xml(1));
			statusCheckTimeoutID = setTimeout("$('#formCheckStatus').submit()", statusCheckFrequency*1000);
		}
	}
}

function statusCheckFailed(responseXML, statusText, xhr, $form) {
// This function is called upon failed completion of an AJAX call checking status

	// We only need to do something if the main form has not finished processing yet.
	if(mainFormSubmitCompleted == 0) {
		$('#statusloadingimg').fadeOut(function() {
			$('#statusImgContainer').append('<img src="' + imagesDir + 'filler.jpg" id="statusfillerimg" />');
			$(this).remove();
		});

		updateStatusDisplay("<status>There was an error in checking the web server for status updates.  This could indicate a problem with your internet connection or with the web server.  We will continue attempts to check for status updates.</status>");

		statusCheckTimeoutID = setTimeout("$('#formCheckStatus').submit()", statusCheckFrequency*1000);
	}
}

function updateStatusDisplay(newStatusText) {
	newStatusText = newStatusText.split("</status><status>");
	newStatusText[0] = newStatusText[0].substring(8);
	var newStatusLastElt = newStatusText.length - 1;
	newStatusText[newStatusLastElt] = newStatusText[newStatusLastElt].substring(0, newStatusText[newStatusLastElt].length - 9);
	var currentDisplays = $('#displayStatus > p');

	if(newStatusText[0] != "Error - could not read status file") {
		var replaceCurrentWithNew = false;
		if(newStatusText.length < currentDisplays.length) {
			replaceCurrentWithNew = true;
		}
		var i = 0;
		while((i < currentDisplays.length) && !replaceCurrentWithNew) {
			if(currentDisplays.eq(i).html() != newStatusText[i]) {
				replaceCurrentWithNew = true;
			}
			i += 1;
		}
		if(replaceCurrentWithNew) {
			$('#displayStatus > p').slideUp(function() {
				$('#displayStatus > p').remove();
				for(var i = 0; i <= newStatusLastElt; i += 1) {
					$('#displayStatus').append($('<p>' + newStatusText[i] + '</p>').hide());
					$('#displayStatus > p').slideDown();
				}
			});
		} else {
			for(var i = currentDisplays.length; i <= newStatusLastElt; i += 1) {
				$('#displayStatus').append($('<p>' + newStatusText[i] + '</p>').hide());
			}
			$('#displayStatus > p:hidden').slideDown();
		}
	}
}

////////////////////////////////////////////////////////////////////////////////
//  END FUNCTIONALITY FOR STATUS UPDATES                                      //
////////////////////////////////////////////////////////////////////////////////