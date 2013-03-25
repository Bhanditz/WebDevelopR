#! /usr/bin/perl -wT
use warnings;
use strict;
use CGI;
use Fcntl qw(:DEFAULT :flock);
use Time::HiRes qw (sleep);
use threads;
use HTML::Entities;



################################################################################
##  ENTER CONFIGURATION INFORMATION HERE:                                     ##

##  Also edit the first line of this script to specify the location of Perl.  ##
##  The line should have the format "#! /path/to/perl -wT"                    ##

##  Use a forward slash to separate directory names in relative web paths.    ##
##  On Linux, also use a forward slash (/) to separate directory names in     ##
##  full system paths.                                                        ##
##  On Windows, use a double backslash (\\) to separate directory names in    ##
##  full system paths.                                                        ##

##  Enter a setting to determine whether file uploads are accepted by the     ##
##  script.  0 (or another false value) means that file uploads are allowed.  ##
##  1 (or another true value) means that file uploads are disabled.           ##
$CGI::DISABLE_UPLOADS = 0;

##  Enter the size restriction (in bytes) for the total upload including any  ##
##  files and other data entered or selections in the web form. For instance, ##
##  a value of 1024*1024 limits the total form submit size to 1 MB.           ##
$CGI::POST_MAX = 1024*1024;

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

##  Enter the full path to the directory where website files for the end user ##
##  should be located (followed by / or \\, depending on the operating system)##
my $results_path = "/var/www/html/results/";

##  Enter the relative web path to the style directory (followed by /)        ##
##  Probably "/style/"                                                        ##
my $style_web_path = "/style/";

##  Enter the relative web path to the images directory (followed by /)       ##
##  Probably "/images/"                                                       ##
my $images_web_path = "/images/";

##  Enter the relative web path to the directory where website files for the  ##
##  end user should be stored (followed by /)                                 ##
##  Probably "/results/"                                                      ##
my $results_web_path = "/results/";

##  Enter the full system path to R, including the executable                 ##
my $R_path = "/usr/bin/R";

##  Enter the full path to GhostScript, including the executable              ##
##  You can typically ignore this unless your R code uses the bitmap function ##
my $GS_path = "/usr/bin/gs";

##  Enter the name of the R script you want to run                            ##
my $R_script = "example-turnkey.R";

##  Enter any directories that need to be in the path when R is called.       ##
##  As far as this script is concerned, this should be "" (an empty string)   ##
##  on Linux, and should be "C:\\Windows\\system32" on Windows.               ##
my $new_path = "";

##  END CONFIGURATION SECTION                                                 ##
################################################################################





################################################################################
#  The real script begins here:                                                #
################################################################################

################################################################################
#  Some general set-up                                                         #
################################################################################

##  "Turn off" buffering - this might cause writing to files to be slower than necessary
##  but it prevents problems with output coming in the wrong order.
$| = 1;


##  Create a cgi object containing the info. from the submitted form
my $query = CGI->new;


##  Start the output to the client.  Output html up through page header text.
print $query->header('text/html');

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
    <h1> $page_header_text </h1>
</div>
HTMLEND


##  Declare a variable which will be used to refer to the thread that prints .'s.
##  We need to declare it up here so we can test on it in the return_error sub.
my $periods_thread;

##  A function which returns an error to the browser and exits the script.
sub return_error{
    my $message = $_[0];
    if(defined($periods_thread)) {
        kill_periods_thread();
    }
        # print HTML page with error message.

print <<"HTMLEND";
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


##  Check to see if there was an error in processing the form submission.
##  If so, return an error, with a slightly more informative message in a couple of cases.
my $error = $query->cgi_error;
if($error) {
    my $errorcode = substr($error, 0, 3);
    if($errorcode eq "400") {
	$error = "ERROR: " . $error . " [it's possible that the form submission was interrupted]";
    } elsif($errorcode eq "413") {
	$error = "ERROR: " . $error . " [the total size of files you selected and/or data you entered in the form exceeds upload limits]";
    } else {
	$error = "ERROR: " . $error;
    }

    return_error($error);
}





################################################################################
#  Get the session ID to be used for this form submit and the R script to call #
################################################################################

##  This code is based on the sample code in the Perl Cookbook, section 7.11
##  Note that we could also use CGI::Session or Apache::Session
##  to generate session id's.  These modules provide nice solutions if we have
##  more complicated requirements.

# Open the file containing the next session ID to use and read the value in.
open FH, "+<$system_path" . "sessionID.txt"    or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
flock(FH, LOCK_EX)                             or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
my $sessionID = <FH> || 0;
if($sessionID == 0) {
    return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
}

# Clean up and de-taint the session ID.
chomp($sessionID);
if($sessionID =~ /^([0-9]+)\z/) {
    $sessionID = $1;
} else {
    return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
}

# Update the session IDs file.
seek(FH, 0, 0)                                 or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
truncate(FH, 0)                                or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
print FH $sessionID+1, "\n"                    or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");
close(FH)                                      or return_error("ERROR: Unable to obtain session ID.  Please contact the website maintainers.");



################################################################################
#  Pre-process the data that was uploaded and output it to local files for R.  #
################################################################################

##  Create a 2-dimensional array containing the submitted data in a format that
##  we can easily output to csv (to be read in by R).
my @uploaded_fields;

# get the names of the submitted parameters
my @params = $query->param;

# $filecount is a count of the number of submitted parameters that are files
my $filecount = 0;

# $paramnum is the number of parameters, starting counting from 0 (we always include the sessionID)
my $paramnum = 0;

# $max_param_length is the length of the longest parameter (# of checkboxes selected, etc.)
my $max_param_length = 1;


##  Add the sessionID to the @uploaded_fields array.
push(@uploaded_fields, ['sessionID', 'nonfile1', $sessionID]);


##  Add all the submitted parameters to the @uploaded_fields array.
foreach my $p (@params) {
	$paramnum++;
	my @temp;
	$temp[0] = $p;

	if($query->uploadInfo($query->param($p))) {
	    # the current parameter is an uploaded file.
	    $temp[1] = 'file';

	    # the location where the file will be temporarily stored
	    # (CGI.pm already stores this in a temp file, but this temp file
	    # is not directly accessible on all systems - for compatibility,
	    # we copy it to a new temp file.)
	    $filecount++;
	    $temp[2] = $system_path . "session" . $sessionID . "-file" . $filecount . ".temp";

	    # the name of the uploaded file
	    my $uploaded_file = $query->param($p);
	    $temp[3] = $uploaded_file;

	    # the content type of the uploaded file
	    $temp[4] = $query->uploadInfo($query->param($p))->{'Content-Type'};

	    # perl's educated guess as to whether we have a binary file or a text file
	    if(-B $query->param($p)) {
		$temp[5] = "binary";
	    } else {
		$temp[5] = "text";
	    }

	    # copy the file to its temporary location

	    # open temp file for output.
	    open TEMP_UPLOADED_FILE, ">" . $temp[2] or
		return_error("ERROR: Unable to create temporary file for uploaded file ${uploaded_file}.  Please contact the website maintainers.");

	    # If we have a binary file, use binary mode to be safe
	    # This is not necessary on all operating systems, but it's never bad
	    if($temp[5] eq "binary") {
		binmode(TEMP_UPLOADED_FILE);
		binmode($uploaded_file);
	    }

	    my $buffer;
	    while(read($uploaded_file, $buffer, 50)) {
		print TEMP_UPLOADED_FILE $buffer;
	    }

	    close(TEMP_UPLOADED_FILE);
	} else {
	    # the current parameter is not an uploaded file.
	    my @values = $query->param($p);
	    $temp[1] = "nonfile" . scalar @values;
	    push(@temp, @values);
	}

	push(@uploaded_fields, [@temp]);
	if($#temp > $max_param_length) {
	    $max_param_length = $#temp;
	}
}


##  print the form entries that were submitted to a local .csv file
my $optionsfile = $system_path . "session" . $sessionID . "-options.csv";
open OPTIONSFILE, ">$optionsfile"
    or return_error("ERROR: Unable to create temporary file for submitted form data.  Please contact the website maintainers.");

for(my $j = 0; $j <= $max_param_length; $j++) {
    print OPTIONSFILE "\"";
    for(my $i = 0; $i <= $paramnum; $i++) {
	if(defined($uploaded_fields[$i][$j])) {
	    $uploaded_fields[$i][$j] =~ s/\"/\"\"/g;
	    print OPTIONSFILE $uploaded_fields[$i][$j];
	}

	if($i < $paramnum) {
	    print OPTIONSFILE "\",\"";
	} else {
	    print OPTIONSFILE "\"\n";
	}
    }
}

close(OPTIONSFILE);



################################################################################
#  Set up the "current status" file                                            #
################################################################################

my $currentstatusfile = $system_path . "session" . $sessionID . "-status.txt";

##  Create the current status file and print an initial status to it.
open CURRENT_STATUS_FILE, ">$currentstatusfile"
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");
print CURRENT_STATUS_FILE "<status>Processing your submission...  Results will be displayed below upon completion.</status>\n"
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");
close(CURRENT_STATUS_FILE)
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");



################################################################################
#  Create a thread that prints a '.' to the browser every second.              #
#  This will prevent the browser and/or web server from timing out,            #
#  so that the connection stays alive while the R script is working.           #
################################################################################

##  The .'s will go into a hidden div so that they are not displayed.
print '<div class="hidden">';

$periods_thread = threads->create('print_periods');

sub print_periods
{
    $SIG{'KILL'} = sub { threads->exit(); };

    while(1) {
        sleep(1);
        print '.';
    }
}

sub kill_periods_thread()
{
    # a function which "kills" the thread that's printing out periods

    $periods_thread->kill('KILL')->detach();

    print "</div>\n";
}



################################################################################
#  Call R to execute the script.                                               #
################################################################################

##  Perl's taint mode insists that when we're going to call external programs,
##  we manually set the path for security reasons.
$ENV{'PATH'} = $new_path;

##  Set up an environment variable to tell R where to find ghost script.
##  This is only necessary if you plan on using the bitmap function.
$ENV{'R_GSCMD'} = $GS_path;

##  Call R to execute the script.  Output from R goes into the @output array.
my @output = `"$R_path" --no-restore --no-save --slave --quiet --args "$optionsfile" "$currentstatusfile" "$results_path" "$results_web_path" < "$R_script"`;



################################################################################
#  Get the most recent status update and print it to the browser.              #
################################################################################

##  Kill the thread that is printing out periods.
kill_periods_thread();


##  Open the status file.
open CURRENT_STATUS_FILE, "<$currentstatusfile"
    or return_error("ERROR: Unable to retrieve status updates.  Please contact the website maintainers.");


##  Output the status to the web browser.
print <<"HTMLEND";
<div class="level1">
    <p class="sectionHeader">Current Status:</p>
    <div id="statusImgContainer">
HTMLEND

print "        <img src=\"$images_web_path" . "filler.jpg\" alt=\"Processing\" id=\"imgStatus\" />\n";

print <<"HTMLEND"; 
    </div>
    <div id="displayStatus">
HTMLEND

while(<CURRENT_STATUS_FILE>) {
    chomp($_);
    print "        <p>" . substr($_, 8, -9) . "</p>\n";
}
close(CURRENT_STATUS_FILE);

print <<"HTMLEND";
    </div>
    <div id="divClear"></div>
</div>
HTMLEND



################################################################################
#  Print the output from R to the browser.                                     #
################################################################################

##  Output the results from R to the web browser.
print <<"HTMLEND";
<div class="level1">
    <p class="sectionHeader">Results:</p>
    <div id="displayResults">
HTMLEND

##  Here's where we output the results from R.
##  We encode characters that are special in HTML when they occur inside of a <pre> tag with a class of ROutput.
my $encode_entities = 0;
foreach my $i (@output) {
    chomp($i);
    if($i =~ /^<\/pre>$/) {
	$encode_entities = 0;
    }
    if($encode_entities) {
	HTML::Entities::encode($i);
    }
    if($i =~ /^<pre class="ROutput">$/) {
	$encode_entities = 1;
    }
    print "$i\n";
}

print <<"HTMLEND";
    </div>
</div>

</div>

</body>
</html>
HTMLEND



################################################################################
#  Clean up old files                                                          #
################################################################################

unlink($optionsfile);
unlink($currentstatusfile);

my @tempfiles = glob($system_path . "session" . $sessionID . "-file*.temp");

foreach my $tempfile (@tempfiles) {
    if($tempfile =~ /^(\Q${system_path}\Esession${sessionID}-file([0-9]+)\.temp)$/) {
	unlink($1);
    }
}
