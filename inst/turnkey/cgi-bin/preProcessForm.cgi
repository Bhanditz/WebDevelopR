#! /usr/bin/perl -wT
use warnings;
use strict;
use CGI;
use Fcntl qw(:DEFAULT :flock);
use Time::HiRes qw (sleep);
use threads;



################################################################################
##  ENTER CONFIGURATION INFORMATION HERE:                                     ##

##  Also edit the first line of this script to specify the location of Perl.  ##
##  The line should have the format "#! /path/to/perl -wT"                    ##

##  On Linux, use a forward slash (/) to separate directory names in          ##
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

##  Enter the full system path to the directory where "system" website files  ##
##  should be located (followed by / or \\, depending on the operating system)##
##  Your webserver must have full permissions for this directory, but it      ##
##  should not be accessible over the internet.                               ##
my $system_path = "/var/WebDevelopRsystem/";

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

##  Print a header to the browser and start the XML structure
print $query->header('text/xml');
print "<?xml version=\"1.0\"?>\n";
print "<!DOCTYPE root>\n";
print "<root>\n";

##  A function which returns an error to the browser and exits the script.
##  Takes one argument: the error message to return.
sub return_error{
    my $message = $_[0];
    print "\n<status>error</status>\n<message>" . $message . "</message>\n</root>";
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
#  Get the session ID to be used for this form submit.                         #
################################################################################

##  This code is based on the sample code in the Perl Cookbook, section 7.11
##  (Note that we could also use CGI::Session or Apache::Session
##  to generate session id's.  These modules provide nice solutions if we have
##  more complicated requirements.)

# Open the file containing the next session ID to use and read the value in.
open FH, "+<$system_path" . "sessionID.txt"    or return_error("ERROR: Unable to obtain session ID.");
flock(FH, LOCK_EX)                             or return_error("ERROR: Unable to obtain session ID.");
my $sessionID = <FH> || 0;
if($sessionID == 0) {
    return_error("ERROR: Unable to obtain session ID.");
}

# Clean up and de-taint the session ID.
chomp($sessionID);
if($sessionID =~ /^([0-9]+)\z/) {
    $sessionID = $1;
} else {
    return_error("ERROR: Unable to obtain session ID.");
}

# Update the session IDs file.
seek(FH, 0, 0)                                 or return_error("ERROR: Unable to obtain session ID.");
truncate(FH, 0)                                or return_error("ERROR: Unable to obtain session ID.");
print FH $sessionID+1, "\n"                    or return_error("ERROR: Unable to obtain session ID.");
close(FH)                                      or return_error("ERROR: Unable to obtain session ID.");



################################################################################
#  Pre-process the data that was uploaded and output it to local files for R.  #
################################################################################

##  Create a 2-dimensional array containing the submitted data in a format that
##  we can easily output to csv (to be read in by R).
my @uploaded_fields;

# get the names of the submitted parameters
my @params = $query->param;

# $paramnum is the number of parameters, starting counting from 0 (we always include the sessionID)
my $paramnum = 0;

# $max_param_length is the length of the longest parameter (# of checkboxes selected, etc.)
my $max_param_length = 0;

# $filecount is the number of files that have been uploaded (of the parameters checked so far)
my $fileCount = 0;

##  Add the sessionID to the @uploaded_fields array.
push(@uploaded_fields, ['sessionID', 'nonfile1', $sessionID]);


##  Add all the submitted parameters to the @uploaded_fields array.
foreach my $p (@params) {
    if($p ne "RScriptToCall") {
	$paramnum++;
	my @temp;
	$temp[0] = $p;

	if($query->uploadInfo($query->param($p))) {
	    # the current parameter is an uploaded file.
	    $temp[1] = 'file';
	    $fileCount++;

	    # the location where the file will be temporarily stored
	    # (CGI.pm already stores this in a temp file, but this temp file
	    # is not directly accessible on all systems - for compatibility,
	    # we copy it to a new temp file.)
	    $temp[2] = $system_path . "session" . $sessionID . "-file" . $fileCount . ".temp";

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
		return_error("ERROR: Unable to create temporary file for uploaded file $uploaded_file");

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
}


##  print the form entries that were submitted to a local .csv file
my $optionsfile = $system_path . "session" . $sessionID . "-options.csv";
open OPTIONSFILE, ">$optionsfile"
    or return_error("ERROR: Unable to create temporary file for submitted form data.");

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
#  Return a success message to the browser, along with the generated session   #
#  ID and the number of files that were uploaded.                              #
################################################################################

print "<status>success</status>\n";
print "<sessionID>" . $sessionID . "</sessionID>\n";
print "</root>";
