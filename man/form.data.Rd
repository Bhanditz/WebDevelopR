\name{form.data}
\alias{form.data}
\title{
The submitted form data.
}
\description{
This function returns a list containing the submitted form data.
}
\usage{
form.data()
}
\value{
The \code{form.data} function returns a list with one component for each field in the submitted form.  The names of the components in this list are taken from the \code{name} attribute of the corresponding form fields in the HTML document.  If the name of the form field in the HTML document begins with a number, it is prepended with an X.  In the case of file upload fields, the corresponding entry in the list contains the full path to the temporary file on the server where the uploaded file was stored (or an empty string if no file was uploaded).  For other form fields, the corresponding component of the list is a vector of submitted values (or an empty string if no options were specified for that form element).  For example, for a group of checkboxes the entry in the list will be a vector of the values of the checkboxes that were selected by the site user.  The returned list also includes one other component: \code{sessionID}, which contains the session ID assigned to the form submission.
}
\seealso{
\code{\link{file.details}}
}
\examples{
\dontrun{
# Suppose the HTML form includes a file selection field named "data"
# and a methods selection field named "methods".  The path to the uploaded
# file and the selected methods can be obtained as follows:
data <- form.data()
file <- data[["data"]]
methods <- data[["methods"]]
}
}
