#! /usr/bin/perl -wT
use warnings;
use strict;
use CGI;
use Fcntl;
use Time::HiRes qw (sleep);
use threads;
use HTML::Entities;



################################################################################
#  ENTER CONFIGURATION INFORMATION HERE                                       ##

##  Also edit the first line of this script to specify the location of Perl.  ##
##  The line should have the format "#! /path/to/perl -wT"                    ##

##  Use a forward slash to separate directory names in relative web paths.    ##
##  On Linux, also use a forward slash (/) to separate directory names in     ##
##  full system paths.                                                        ##
##  On Windows, use a double backslash (\\) to separate directory names in    ##
##  full system paths.                                                        ##

##  Enter the full path to the directory where website files for the end user ##
##  should be located (followed by / or \\, depending on the operating system)##
my $results_path = "/var/www/html/results/";

##  Enter the full system path to the directory where "system" website files  ##
##  should be located (followed by / or \\, depending on the operating system)##
##  Your webserver must have full permissions for this directory, but it      ##
##  should not be accessible over the internet.                               ##
my $system_path = "/var/WebDevelopRsystem/";

##  Enter the relative web path to the directory where website files for the  ##
##  end user are located (followed by a /)                                    ##
##  Probably "/results/"                                                      ##
my $results_web_path = "/results/";

##  Enter the full path to R, including the executable                        ##
my $R_path = "/usr/bin/R";

##  Enter the full path to GhostScript, including the executable              ##
##  You can typically ignore this unless your R code uses the bitmap function ##
my $GS_path = "/usr/bin/gs";

##  Enter the name of the R script you want to run                            ##
my $R_script = "example-turnkey.R";

##  Enter any directories that need to be in the path when R is called.       ##
##  As far as this script is concerned, this should be "" (en ampty string)   ##
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

##  Files will not be uploaded to this CGI script.
$CGI::DISABLE_UPLOADS = 1;

##  The maximum size of parameters submitted to this CGI script is small.
$CGI::POST_MAX = 5*1024;

##  Create a CGI object containing the info. from the submitted form
my $query = CGI->new;


##  Print a header to the web browser and start the XML structure
print $query->header('text/xml');
print "<?xml version=\"1.0\"?>\n";
print "<root>\n";


##  Get and de-taint the session ID.
##  Only the digits 0-9 are allowed in these fields (i.e., no letters or other characters are allowed)
my $sessionID = $query->param('sessionID');
if($sessionID =~ /^([0-9]+)\z/) {
    $sessionID = $1;
} else {
    return_error("ERROR: The session ID submitted was invalid.  Please contact the website maintainers.");
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
    print "\n<status>error</status>\n<message>" . $message . "</message>\n</root>";
    exit;
}



################################################################################
#  Set up the "current status" file                                            #
################################################################################

my $currentstatusfile = $system_path . "session" . $sessionID . "-status.txt";

##  Create the current status file and print an initial status to it.
open CURRENT_STATUS_FILE, ">$currentstatusfile"
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");
print CURRENT_STATUS_FILE "<status>Processing your submission...</status>\n"
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");
close(CURRENT_STATUS_FILE)
    or return_error("ERROR: Unable to create temporary file for status updates.  Please contact the website maintainers.");



################################################################################
#  Create a thread that prints a '.' to the browser every second.              #
#  This will prevent the browser and/or web server from timing out,            #
#  so that the connection stays alive while the R script is working.           #
################################################################################

##  The .'s will go into a junk XML tag.
print '<junk>';

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

    print "</junk>\n";
}



################################################################################
#  Call R and print the output to the browser.                                 #
################################################################################

##  Perl's taint mode insists that when we're going to call external programs,
##  we manually set the path for security reasons.
$ENV{'PATH'} = $new_path;

##  Set up environment variable to tell R where to find ghost script
$ENV{'R_GSCMD'} = $GS_path;

## The file with the submitted form data.
my $optionsfile = $system_path . "session" . $sessionID . "-options.csv";

##  Call R to execute the script.  Output from R goes into the @output array.
my @output = `"$R_path" --no-restore --no-save --slave --quiet --args "$optionsfile" "$currentstatusfile" "$results_path" "$results_web_path" < "$R_script"`;


##  Kill the thread that's printing a period every 20 seconds.
kill_periods_thread();


##  Print the output from R to the web browser.
##  We encode characters that are special in HTML when they occur inside of a <pre> tag.
my $encode_entities = 0;
print "<contents>\n";

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

print "</contents>\n";


################################################################################
#  Get the most recent status update and print it to the browser.              #
################################################################################

open CURRENT_STATUS_FILE, "<$currentstatusfile"
    or return_error("ERROR: Unable to retrieve status updates.  Please contact the website maintainers.");

while(<CURRENT_STATUS_FILE>) {
    print $_;
}

close(CURRENT_STATUS_FILE);

print "</root>";



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
