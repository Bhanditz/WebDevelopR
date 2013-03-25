########################################################################################
# This is an example R file that can be used with example-dev.html. The main purpose   #
# of this script is to show how to access the user input from the html form.           #
########################################################################################


################################################################################
##  Enter configuration information

# The location where the uploaded file was stored
FILE_READ_DIR <- '/var/www/system/'

# The location where the plot should be stored
RESULTS_DIR <- '/var/www/html/results/'

# The relative web path to the location where the plot is stored
WEB_PATH_RESULTS_DIR <- '/results/'

##  END configuration information entry
################################################################################

library("WebDevelopR")

# The form in sample.html contains input fields for
# "xVar", "yVar", "method", and "firstSessionID".
# This R file can access these inputs through the elements
# associated with each of those names of the list returned by form.data.
submitted.data <- form.data()

# Read in data from the previously uploaded file.
load(paste(FILE_READ_DIR, 'session', submitted.data[["firstSessionID"]],
  '-loaded-data.RData', sep=''))

# Obtain the variables for the x and y axes of the plot selected
# by the user.
x_var <- submitted.data[["xVar"]]
y_var <- submitted.data[["yVar"]]

# Obtain the plot type for the plot selected by the user
if(submitted.data[["method"]] == "line") {
	method = 'l'
} else {
	method = 'p'
}

# Create the plot
png(paste(RESULTS_DIR, "session", submitted.data[["sessionID"]], "-",
  "image.png", sep = ""), width = 600, height = 600);
plot(data[, x_var], data[, y_var], type = method, xlab = x_var, ylab = y_var)
garbage <- dev.off()

# Output an image tag which will be inserted into the web page.
cat("<imgTagContainer>\n");
cat("<img src=\"", WEB_PATH_RESULTS_DIR, "session", submitted.data[["sessionID"]],
  "-image.png\" width=\"100%\" ></img>\n", sep = "");
cat("</imgTagContainer>");
