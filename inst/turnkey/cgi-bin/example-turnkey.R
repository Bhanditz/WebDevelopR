library("WebDevelopR")

########### Accessing the user input ###############

# The form in sample.html contains input fields named
# "data", "title", "description", "methods", and "plot".

submitted.data <- form.data()

file <- submitted.data[["data"]]
title <- submitted.data[["title"]]
description <- submitted.data[["description"]]
methods <- submitted.data[["methods"]]
plot <- submitted.data[["plot"]]

############ Using the utility functions ###########

# Status updates are shown in a separate section than the
# results.  The append=FALSE argument means that any previously
# logged status updates are removed.
status.update("Processing your submission...", append=FALSE)

if(sum(methods == "sd" | methods == "var") == 0) {
  status.update("Error: You must select a type of spread.")
  quit("no")
}

if(length(file.details()) == 0) {
  data <- data.frame(x = sample(1:5,5,TRUE),
    y = sample(1:5,5,TRUE), z = sample(1:5,5,TRUE))
  status.update("No file provided. Using random data...",
    append = TRUE)
} else {
  data <- read.csv(file)
}

# You can print strings directly to the results section using
# the cat function.
cat("This is the", title, "analysis.", description,
  "R used the following dataset:")

# web.print displays a nicely formatted version of R's print.
# The argument is a list of objects to print.
web.print(list(data))

results <- list()

# The elements of "methods" are taken from the "value"
# attributes of the inputs that the user selected (specified in
# the HTML code).
for(m in methods) {
  if(m == "mean") {
    results$mean = apply(data, 2,
      function(x) {mean(as.numeric(x))})
  } else if(m == "median") {
    results$median = apply(data, 2,
      function(x) {median(as.numeric(x))})
  } else if(m == "sd") {
    results$spread = apply(data, 2, sd)
  } else if(m == "var") {
    results$spread = apply(data, 2, var)
  }
}

results <- data.frame(results)

# The web.png and web.jpeg functions embed graphics into the
# results section displayed to the user.
if(plot == "png") {
  ### The alt text is displayed if the image cannot be viewed.
  web.png("results.png", attributes.text = "alt=\"Results\"",
    width = 600, height = 300)
  barplot(results$spread, names.arg = names(data),
    main = "column spread")
  garbage <- dev.off()
} else {
  web.jpeg("results.jpeg", attributes.text = "alt=\"Results\"",
    width = 600, height = 300)
  barplot(results$spread, names.arg = names(data),
    main = "column spread")
  garbage <- dev.off()
}

# web.csv creates a link to a file that the user can download.
web.csv(results, "results.csv", before.link.text = "Click ",
  link.text = "here",
  after.link.text = " to download the rest of your analysis.",
  open.new.window = FALSE, enclose.in.p = FALSE)

status.update("Analysis complete.", append = TRUE)
