\name{status.update}
\alias{status.update}
\title{
Provide status updates to the website user.
}
\description{
This function is used to provide status updates to the website user.
}
\usage{
status.update(status, append = FALSE)
}
\arguments{
  \item{status}{
A string containing the status message to be displayed to the site user.
}
  \item{append}{
A logical value.  If true, the status will be appended to previous status updates; if false, it will replace previous status updates.
}
}
\details{
This function is only useful for the ``Complete'' version of the WebDevelopR package.  The function writes status update text to the session-specific temporary file used for storing status updates.  These updates are automatically retrieved and displayed by the user's browser while the R script is running.  This is useful if the script takes a long time to complete.
}
\value{
None.
}
\examples{
\dontrun{
status.update("Processing your submission - Stage 1")
status.update("Processing your submission - Stage 2", append=TRUE)
}
}