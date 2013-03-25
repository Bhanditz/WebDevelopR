#! /usr/bin/perl -wT
use warnings;
use strict;
use CGI;
use Fcntl;
use Time::HiRes qw (sleep);



################################################################################
##  ENTER CONFIGURATION INFORMATION HERE:                                     ##

##  Also edit the first line of this script to specify the location of Perl.  ##
##  The line should have the format "#! /path/to/perl -wT"                    ##

##  On Linux, use a forward slash (/) to separate directory names in          ##
##  full system paths.                                                        ##
##  On Windows, use a double backslash (\\) to separate directory names in    ##
##  full system paths.                                                        ##

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

##  "turn off" buffering - this might cause writing to files to be slower than necessary
##  but it prevents problems with output coming in the wrong order.
$| = 1;

##  Define some useful functions

sub return_error
{
# This function is called if an error occurs when we try to read from the status file
	print "<status>Error - could not read status file</status>\n</root>";
	exit;
}

sub get_lock
{
# This function gets a lock on the status file.  Since R doesn't have functionality built in to work with "real" file locks,
# we create a file called "filename.lock" indicating that we have locked the file.

    my $lockfile = $_[0] . ".lock";
    my $gotlock = 0;
    my $trycount = 0;
    while(!$gotlock) {
	$trycount++;
	$gotlock = 1;
	sysopen(LOCKFILE, $lockfile, O_WRONLY | O_EXCL | O_CREAT) or $gotlock = 0;
	if($trycount > 5 && !$gotlock) {
	    return_error();
	}
	if(!$gotlock) {
	    sleep(0.5);
	}
    }
    print LOCKFILE "statuscheck";
    close(LOCKFILE);
}

sub unlock
{
# This function deletes the "file.lock" file, thereby removing the lock on the file.

    unlink($_[0] . ".lock") or return_error();
}

sub unlock_and_return_error
{
# This function calls unlock to unlock the file, and then returns an error.

    unlock($_[0]);
    return_error();
}


##  Create a cgi object containing the info. from the submitted form and de-taint submitted values
my $query = CGI->new;

my $sessionID = $query->param('sessionID');
if($sessionID =~ /^([0-9]+)\z/) {
    $sessionID = $1;
} else {
    return_error();
}


##  Start output to the browser
# print a header to the web browser and start xml document
print $query->header('text/xml');
print "<?xml version=\"1.0\"?>\n";

print "<root>\n";


##  Open the status file and send its contents to the browser
my $statusfile = $system_path . "session" . $sessionID . "-status.txt";

get_lock($statusfile);

open STATUSFILE, "<$statusfile" or unlock_and_return_error($statusfile);

#Print its contents to the web browser
while(<STATUSFILE>)
{
	print $_;
}

unlock($statusfile);

print "\n</root>";
