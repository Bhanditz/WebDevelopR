\name{web.png}
\alias{web.png}
\alias{web.jpeg}
\title{
Create a graphic and display it on the web page.
}
\description{
Used to create .png and .jpeg image files, and to embed these images in the results page.
}
\usage{
web.png(file.name = "image.png", attributes.text = "", centered = TRUE, ...)

web.jpeg(file.name = "image.jpeg", attributes.text = "", centered = TRUE, ...)
}
\arguments{
  \item{file.name}{
The name of the image file, NOT including a directory to store it in.
}
  \item{attributes.text}{
This text will be used for the attributes text of the HTML image tag.
}
  \item{centered}{
Indicates whether the image should be centered when it is displayed to the user in the results page.
}
  \item{\dots}{
Arguments to \code{jpeg} or \code{png}, respectively.
}
}
\details{
These functions are wrappers for \code{png} and \code{jpeg}.  The functions store the image file in the results directory for your web server (this directory is specified in the configuration section at the top of the processForm.cgi and R.cgi CGI scripts).  They also create the necessary HTML tags to insert the image into the results page that is displayed to the site user.

The created image file will not be deleted automatically.  You should periodically review files in the results directory and clear old ones out.

In order to display the correct images to each web site user, \code{file.name} will be pre-pended with ``session'', the session ID, and a dash.  For example, if you call \code{web.jpeg} with the default argument of \code{file.name = "image.jpeg"}, and the session ID is 23, the file name actually used for the image will be \code{"session23-image.jpeg"}.
}
\value{
None.
}
\examples{
\dontrun{
web.png("plot.png", attributes.text="alt=\"Your Plot\"", width=600, height=300)
plot(x=rnorm(10), y=rnorm(10))
points(x=0, y=0, pch="+", col="red")
garbage <- dev.off() # capture the output from calling dev.off to prevent it from
                     # being displayed in the results page

web.jpeg("plot.jpeg", attributes.text="alt=\"Your Plot\"", width=600, height=300)
plot(x=rnorm(10), y=rnorm(10))
points(x=0, y=0, pch="+", col="red")
garbage <- dev.off() # capture the output from calling dev.off to prevent it from
                     # being displayed in the results page
}
}