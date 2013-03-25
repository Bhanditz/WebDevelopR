#! /usr/bin/perl -wT
use warnings;
use strict;
use CGI;
use Fcntl;
use Time::HiRes qw (sleep);
use threads;



################################################################################
##  ENTER CONFIGURATION INFORMATION HERE:                                     ##

##  Also edit the first line of this script to specify the location of Perl.  ##
##  The line should have the format "#! /path/to/perl -wT"                    ##

##  Use a forward slash to separate directory names in relative web paths.    ##
##  On Linux, also use a forward slash (/) to separate directory names in     ##
##  full system paths.                                                        ##
##  On Windows, use a double backslash (\\) to separate directory names in    ##
##  full system paths.                                                        ##

##  Enter the title of the results page                                       ##
##  Typically appears in the tab or bar at the top of the web browser         ##
my $results_page_title = "Your Page Title Here - Results";

##  Enter the page header text for the results page here                      ##
##  Appears in bold letters near the top of the page                          ##
my $page_header_text = "Your Page Header Here - Results";

##  Enter the full system path to the directory where "system" website files  ##
##  should be located (followed by / or \\, depending on the operating system)##
##  Your webserver must have full permissions for this directory, but it      ##
##  should not be accessible over the internet.                               ##
my $system_path = "/var/WebDevelopRsystem/";

##  Enter the relative web path to the style directory (followed by /)        ##
##  Probably "/style/"                                                        ##
my $style_web_path = "/style/";

##  Enter the relative web path to the images directory (followed by /)       ##
##  Probably "/images/"                                                       ##
my $images_web_path = "/images/";

##  Enter the relative web path to the scripts directory (followed by /)      ##
##  Probably "/scripts/"                                                      ##
my $scripts_web_path = "/scripts/";

##  Enter the relative web path to the cgi-bin directory (followed by /)      ##
##  Probably "/cgi-bin/"                                                      ##
my $cgibin_web_path = "/cgi-bin/";

##  END CONFIGURATION SECTION                                                 ##
################################################################################





################################################################################
##  The real script begins here:                                              ##
################################################################################

##  "Turn off" buffering - this might cause writing to files to be slower than necessary
##  but it prevents problems with output coming in the wrong order.
$| = 1;

##  Files will not be uploaded to this CGI script.
$CGI::DISABLE_UPLOADS = 1;

##  The maximum size of parameters submitted to this CGI script is small.
$CGI::POST_MAX = 5*1024;

##  Create a CGI object containing the info. from the submitted form
my $query = CGI->new;

##  Print a header to the web browser
print $query->header('text/html');

##  A function which returns an error to the browser and exits the script.
sub return_error {
    my $message = $_[0];

    # Print HTML page with error message.

print <<"HTMLEND";
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" > 

<head>

<title>$results_page_title</title>

<style type="text/css" title="currentStyle" media="screen"> 
    \@import "${style_web_path}style.css";
</style>

</head>

<body>

<div id="contents">

<div class="level1">
    <h1>$page_header_text</h1>
</div>

<div class="level1">
    <p class="sectionHeader">Current Status:</p>
    <div id="displayStatus">
        <img src="${images_web_path}redx.jpg" alt="Error" />
	<span>$message</span>
    </div>
</div>

</div>

</body>
</html>
HTMLEND

    # Exit the script.
    exit;

}


##  Get and de-taint the session ID.
##  Only the digits 0-9 are allowed in these fields (i.e., no letters or other characters are allowed)
my $sessionID = $query->param('sessionID');
if($sessionID =~ /^([0-9]+)\z/) {
    $sessionID = $1;
} else {
    return_error("ERROR: The session ID submitted was invalid.  Please contact the website maintainers.");
}



##  Print a web page to the browser which will load the results.
print <<"HTMLEND";
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" > 

<head>

<title>$results_page_title</title>

<style type="text/css" title="currentStyle" media="screen"> 
    \@import "${style_web_path}style.css";
</style>

<script type="text/javascript" src="${scripts_web_path}jquery-1.6.2.min.js"></script>
<script type="text/javascript" src="${scripts_web_path}jquery.form.js"></script>
<script type="text/javascript" src="${scripts_web_path}jquery.xml.js"></script>
<script type="text/javascript" src="${scripts_web_path}resultsScript.js"></script>

</head>

<body>

<div id="contents">

<div class="level1">
    <h1>$page_header_text</h1>
</div>

<div class="hidden">
    <img src="${images_web_path}filler.jpg" />
</div>

<div class="level1">
    <p class="sectionHeader">Current Status:</p>
    <div id="statusImgContainer">
        <img src="${images_web_path}loadinfo.gif" alt="Processing" id="statusloadingimg" />
    </div>

    <div id="displayStatus">
        <p>Processing your submission...</p>
    </div>
    <div id="divClear"></div>
</div>

<div id="hidden">
    <form id="formCallR" method="POST" action="${cgibin_web_path}R.cgi" enctype="multipart/form-data">
        <input type="hidden" name="sessionID" value="$sessionID" />
    </form>
    <form id="formCheckStatus" method="POST" action="${cgibin_web_path}statusCheck.cgi" enctype="multipart/form-data">
        <input type="hidden" name="sessionID" value="$sessionID" />
    </form>
</div>

</div>

</body>
</html>
HTMLEND
