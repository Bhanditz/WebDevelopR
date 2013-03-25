\name{web.table}
\alias{web.table}
\alias{web.csv}
\alias{web.csv2}
\title{
Create a link to a data file.
}
\description{
Prints a data frame or matrix to a text file and inserts a link to the file in the results page displayed to the website user.
}
\usage{
web.table(x, file.name = "table.txt", before.link.text = "Click ", link.text = "here",
    after.link.text = " to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)",
    open.new.window = TRUE, attributes.text = "", enclose.in.p = TRUE, ...)

web.csv(x, file.name = "table.csv", before.link.text = "Click ", link.text = "here",
    after.link.text = " to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)",
    open.new.window = TRUE, attributes.text = "", enclose.in.p = TRUE, ...)

web.csv2(x, file.name = "table.csv", before.link.text = "Click ", link.text = "here",
    after.link.text = " to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)",
    open.new.window = TRUE, attributes.text = "", enclose.in.p = TRUE, ...)
}
\arguments{
  \item{x}{
The object to be written to a file.  This is passed on to the \code{write.table}, \code{write.csv}, or \code{write.csv2} function, which prefer that \code{x} be a matrix or data frame.  If it is another data type, an attempt is made to coerce \code{x} to a data frame.
}
  \item{file.name}{
The name of the output file.
}
  \item{before.link.text}{
Text to be displayed in the results page immediately before the link.
}
  \item{link.text}{
The clickable text displayed in the results page as a link to the output file.
}
  \item{after.link.text}{
Text to be displayed in the results page immediately after the link.
}
  \item{open.new.window}{
Indicates whether the link should be set to open in a new window.  The default is \code{TRUE}.
}
  \item{attributes.text}{
Attributes text for the HTML link.
}
  \item{enclose.in.p}{
If \code{TRUE}, \code{before.link.text}, the link, and \code{after.link.text} are all placed within a paragraph HTML element.  Otherwise, this text is not placed within a block level HTML element.
}
  \item{\dots}{
Arguments to \code{write.table}, \code{write.csv}, or \code{write.csv2}.
}
}
\details{
These functions are wrappers for \code{write.table}, \code{write.csv}, and \code{write.csv2}.  The functions store the output file in the results directory for your web server (this directory is specified in the configuration section at the top of the processForm.cgi and R.cgi CGI scripts).  They also create the necessary HTML tags to insert a link to the output file into the results page that is displayed to the site user.

The created data file will not be deleted automatically.  You should periodically review files in the results directory and clear old ones out.

In order to display the correct images to each web site user, \code{file.name} will be pre-pended with ``session'', the session ID, and a dash.  For example, if you call \code{web.csv} with the default argument of \code{file.name = "table.csv"}, and the session ID is 23, the file name actually used for the image will be \code{"session23-table.csv"}.
}
\value{
None.
}
\examples{
\dontrun{
data(iris)
web.table(iris, "iris.txt")
web.csv(iris, "iris.csv")
web.csv2(iris, "iris2.csv")
}
}