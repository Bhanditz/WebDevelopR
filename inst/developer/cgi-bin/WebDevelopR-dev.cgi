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

##  Enter the full path to R, including the executable                        ##
my $R_path = "/usr/bin/R";

##  Enter the full path to GhostScript, including the executable              ##
##  You can typically ignore this unless your R code uses the bitmap function ##
my $GS_path = "/usr/bin/gs";

##  Enter the name(s) of the R scripts you want to be able to run, separated  ##
##  by commas.                                                                ##
my $R_scripts = "example-dev1.R,example-dev2.R";

##  Enter the data type you would like to return - "HTML", "XML", or "JSON"   ##
my $data_type = "XML";

##  Enter any directories that need to be in the path when R is called.       ##
##  As far as this script is concerned, this should be "" (an ampty string)   ##
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
if($data_type eq "HTML") {
	print $query->header('text/html');

	print <<"HTMLEND";
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
		"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" > 
HTMLEND
} elsif($data_type eq "XML") {
	print $query->header('text/xml');
	print "<?xml version=\"1.0\"?>\n";
	print "<root>\n";
} elsif($data_type eq "JSON") {
	print $query->header('application/json');
} else {
	print $query->header('text/html');

	print <<"HTMLEND";
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
		"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" > 
	<body>
	<div class="error">
		<p>Error: Incorrectly specified data type.</p>
	</div>
	</body>
	</html>
HTMLEND
}


##  Declare a variable which will be used to refer to the thread that prints .'s.
##  We need to declare it up here so we can test on it in the return_error sub.
my $periods_thread;

##  A function which returns an error to the browser and exits the script.
sub return_error{
	my $message = $_[0];
	if(defined($periods_thread)) {
		kill_periods_thread();
	}

	if($data_type eq "HTML") {
		# print HTML with error message.
		print <<"HTMLEND";
<body>

    <div class="error">
        $message
    </div>

</body>

</html>
HTMLEND
	} elsif($data_type eq "XML") {
		print "<error> $message </error>\n</root>";
	} elsif($data_type eq "JSON") {
		print "{ \"error\": { \"message\": $message }}";
	}

	# Exit the script.
	exit;
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


# Get the name of the R script to call.
my $submitted_script = $query->param('RScriptToCall');
my $R_script = "";

if(defined $submitted_script) {
    foreach my $valid_script (split(/,/, $R_scripts)) {
	$valid_script =~ s/^\s+//;
	$valid_script =~ s/\s+$//;
	if($submitted_script eq $valid_script) {
	    $R_script = $valid_script;
	}
    }
} else {
    return_error("ERROR: No R script was specified.  Please contact the website maintainers.");
}

if($R_script eq "") {
    return_error("ERROR: The requested R script was invalid.  Please contact the website maintainers.");
}



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
    if($p ne "RScriptToCall") {
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
#  Create a thread that prints a '.' to the browser every second.              #
#  This will prevent the browser and/or web server from timing out,            #
#  so that the connection stays alive while the R script is working.           #
#  We sleep only 1 second so that we never have to wait longer than 1 sec      #
#  to return after the R script has finished running.                          #
################################################################################

##  The .'s will go into a hidden div so that they are not displayed.
if($data_type eq "HTML") {
	print '<div id="periodsContainer" style="display: none;">';
} elsif($data_type eq "XML") {
	print "<periodsContainer>\n";
} elsif($data_type eq "JSON") {
	print "{ \"periodsContainer\": { \"periods\": \"";
}

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

    if($data_type eq "HTML") {
	print "</div>\n";
    } elsif($data_type eq "XML") {
	print "</periodsContainer>\n";
    } elsif($data_type eq "JSON") {
	print "\" }}\n";
    }
}



################################################################################
#  Call R to execute the script and print output from R to the browser.        #
################################################################################

##  Perl's taint mode insists that when we're going to call external programs,
##  we manually set the path for security reasons.
$ENV{'PATH'} = $new_path;

##  Set up an environment variable to tell R where to find ghost script.
$ENV{'R_GSCMD'} = $GS_path;

##  Call R to execute the script.  Output from R goes into the @output array.
my @output = `"$R_path" --no-restore --no-save --slave --quiet --args "$optionsfile" < "$R_script"`;

##  Kill the thread that is printing out periods.
kill_periods_thread();

##  Here's where we output the results from R.
foreach my $i (@output) {
    chomp($i);
    print "$i\n";
}

##  Close out the HTML/XML document tags
if($data_type eq "HTML") {
	print "</html>\n";
} elsif($data_type eq "XML") {
	print "</root>\n";
}


################################################################################
#  Clean up temporary files                                                    #
################################################################################

unlink($optionsfile);

my @tempfiles = glob($system_path . "session" . $sessionID . "-file*.temp");

foreach my $tempfile (@tempfiles) {
    if($tempfile =~ /^\Q${system_path}\Esession${sessionID}-file([0-9]+)\.temp$/) {
	unlink($1);
    }
}
