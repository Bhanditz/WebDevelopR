\name{file.details}
\alias{file.details}
\title{
Details about uploaded files.
}
\description{
This function returns a list with some details about each uploaded file.
}
\usage{
file.details()
}
\details{
The list returned by \code{file.details} only contains entries for form fields where a file was selected.
}
\value{
For each uploaded file, this list contains a vector of three values:
\enumerate{
  \item \code{file.name} is the original file name of the uploaded file (including the extension),
  \item \code{content.type} is the MIME content type of the file, and
  \item \code{text.or.binary} is Perl's educated guess as to whether the uploaded file is a text or binary file.  Either ``text'' or ``binary''.
}
}
\seealso{
\code{\link{form.data}}
}
\examples{
\dontrun{
# Suppose the HTML form includes a file selection field named "data"
# More information about the uploaded file can be obtained as follows:
details <- file.details()[["data"]]
}
}
