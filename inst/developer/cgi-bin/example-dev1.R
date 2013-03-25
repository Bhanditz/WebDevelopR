################################################################
##  Enter configuration information

# The location where the uploaded file will be stored
FILE_WRITE_DIR <- '/var/www/system/'

##  END configuration information entry
################################################################

library("WebDevelopR")

# The form in sample-core.html contains the input field
# "data".  This R script can access that input through the
# form.data or file.details functions.
# It can also access the sessionID through form.data.
submitted.data <- form.data()

sessionID = submitted.data[["sessionID"]]

# Save the data file so that it can be accessed by the second R
# script in order to create the plot. We put the session ID in 
# the file name so that the file won't be overwritten by
# another user's submission.
file <- submitted.data[["data"]]
data <- read.csv(file)
save(data, file = paste(FILE_WRITE_DIR, 'session', sessionID,
  '-loaded-data.RData', sep=''))

# Output some XML with the names of variables in the uploaded
# data file. This will be used to populate the drop-down menus
# on the web page.
variables <- colnames(data)

for(i in 1:length(variables)) {
	cat("<var",i,">",variables[i],"</var",i,">\n",sep='')
}

# Output some XML with the sessionID.  We need to pass this on
# to the second R script so that it can read in the correct
# data file.
cat("<sessionID>",sessionID,"</sessionID>",sep='')
