\name{web.print}
\alias{web.print}
\title{
Print objects to a web page.
}
\description{
Prints objects in a <pre> ... </pre> HTML environment (similar to verbatim in LaTeX).
}
\usage{
web.print(objects, width = 80, leading.spaces.num = 2,
    continued.line.indent.num = 8)
}
\arguments{
  \item{objects}{
A list of objects to print.
}
  \item{width}{
Number of characters per line (not including \code{leading.spaces.num} but including \code{continued.line.indent.num}).
}
  \item{leading.spaces.num}{
Number of spaces to insert before each line.  These spaces create some padding in the user display.
}
  \item{continued.line.indent.num}{
If a line of more than \code{width} characters is broken, the number of extra spaces to insert before the continued line.}
}
\details{
\code{web.print} allows you to send the result of a call to the \code{print} function to the user's web browser.  The output is embedded in a \code{<pre>} tag, which is displayed in the browser with a fixed width font and a shaded background.  Note that objects is iterated over and every component is printed; if you don't embed the objects you want to print in a list, this could result in some funny behavior.  This is done to allow you to print multiple objects within the same shaded area on the results page.}
\value{
None.
}
\examples{
\dontrun{
data(iris)
web.print(iris$Petal.Length) # prints each component of the vector of petal lengths
                             # on a separate line
web.print(list(iris$Petal.Length)) # probably want you wanted
}
}