WebDevelopR.vars <- list(form.data = NULL,
	file.details = NULL,
	status.file.path = NULL,
	full.sys.results.path = NULL,
	rel.web.results.path = NULL)


.onLoad <- function(libname, pkgname) {
	# Get the parameters passed in through command line arguments
	#  - locations of important files
	#  - submitted data from web form
	cmd.args <- commandArgs(trailingOnly = TRUE)

	penv <- parent.env(environment())

	if(length(cmd.args) == 0) {
		warning("No command line arguments to R available when loading package WebDevelopR.")
	} else {
		if(length(cmd.args) > 1) {
			# if necessary, append a / to the results directory path
			if(!(substr(cmd.args[3], nchar(cmd.args[3]), nchar(cmd.args[3])) %in% c("/", "\\"))) {
				cmd.args[3] <- paste(cmd.args[3], "/", sep="")
			}

			penv$WebDevelopR.vars$status.file.path <- cmd.args[2]
			penv$WebDevelopR.vars$full.sys.results.path <- cmd.args[3]
			penv$WebDevelopR.vars$rel.web.results.path <- cmd.args[4]
		}

		# read in the data from the submitted web form
		options.file <- cmd.args[1]
		params <- read.csv(options.file, stringsAsFactors=FALSE)

		temp.form.data <- list()
		temp.file.details <- list()

		for(param in names(params)) {
			if(params[[param]][1] == "file") {
				temp.form.data[[param]] <- params[[param]][2]
				temp.file.details[[param]] <- params[[param]][3:5]
				names(temp.file.details[[param]]) <- c("file.name", "content.type", "text.or.binary")
			} else {
				n.entries <- as.integer(substring(params[[param]][1], first=8)) + 1
				temp.form.data[[param]] <- params[[param]][2:n.entries]
			}
		}

		penv$WebDevelopR.vars$form.data <- temp.form.data
		penv$WebDevelopR.vars$file.details <- temp.file.details
	}
}

get.lock <- function(file) {
	got.lock <- FALSE
	try.count <- 0
	temp.lock.file <- paste(file,".lock.temp",sep="",collapse="")
	real.lock.file <- paste(file,".lock",sep="",collapse="")
	while(!got.lock && try.count < 5) {
		try.count <- try.count + 1
		tryCatch({
			temp <- file.create(temp.lock.file)
			cat("R",file=temp.lock.file)
			got.lock <- file.copy(from = temp.lock.file, to=real.lock.file, overwrite=FALSE)
		}, error = function (e) {
			got.lock <- FALSE
		}, finally = {
			temp <- file.remove(temp.lock.file)
			if(!got.lock) {
				Sys.sleep(0.5)
			}
		})
	}
	return(got.lock)
}

unlock <- function(file) {
	temp <- file.remove(paste(file,".lock",sep="",collapse=""))
}

file.details <- function() {
	return( (parent.env(environment())$WebDevelopR.vars)$file.details )
}

form.data <- function() {
	return( (parent.env(environment())$WebDevelopR.vars)$form.data )
}

status.update <- function(status, append=FALSE) {
	status.file <- (parent.env(environment())$WebDevelopR.vars)$status.file.path

	if(is.null(status.file)) {
		warning("No file is available for status updates.")
	} else {
		#write new status to the status file
		if(get.lock(status.file)) {
			cat("<status>",status,"</status>\n",file=status.file,sep="",append=append)
			unlock(status.file)
		}
	}
}


web.png <- function(file.name="image.png", attributes.text="", centered=TRUE, ...) {
	sys.results.path <- (parent.env(environment())$WebDevelopR.vars)$full.sys.results.path
	web.results.path <- (parent.env(environment())$WebDevelopR.vars)$rel.web.results.path
	session.ID <- ((parent.env(environment())$WebDevelopR.vars)$form.data)$sessionID

	if(is.null(sys.results.path) || is.null(web.results.path)) {
		warning("Path to the results directory is not available.")
	} else {
		png(paste(sys.results.path, "session", session.ID, "-", file.name, sep=""), ...);
		if(centered == TRUE) {
			cat("<div class=\"centeredContentContainer\">\n");
		}
		cat("<img src=\"", web.results.path, "session", session.ID, "-", file.name, "\" ", attributes.text, " ></img>\n", sep="");
		if(centered == TRUE) {
			cat("</div>\n");
		}
	}
}


web.jpeg <- function(file.name="image.jpeg", attributes.text="", centered=TRUE, ...) {
	sys.results.path <- (parent.env(environment())$WebDevelopR.vars)$full.sys.results.path
	web.results.path <- (parent.env(environment())$WebDevelopR.vars)$rel.web.results.path
	session.ID <- ((parent.env(environment())$WebDevelopR.vars)$form.data)$sessionID

	if(is.null(sys.results.path) || is.null(web.results.path)) {
		warning("Path to the results directory is not available.")
	} else {
		jpeg(paste(sys.results.path, "session", session.ID, "-", file.name, sep=""), ...);
		if(centered == TRUE) {
			cat("<div class=\"centeredContentContainer\">\n");
		}
		cat("<img src=\"", web.results.path, "session", session.ID, "-", file.name, "\" ", attributes.text, " ></img>\n", sep="");
		if(centered == TRUE) {
			cat("</div>\n");
		}
	}
}


web.print <- function(objects, width=80, leading.spaces.num=2, continued.line.indent.num=8) {
	options(width=width);
	leading.spaces <- paste(rep(" ", leading.spaces.num), collapse="");
	continued.line.leading.spaces <- paste(rep(" ", leading.spaces.num + continued.line.indent.num), collapse="");

	output <- capture.output(for(object in objects) { print(object); });
	output <- paste(leading.spaces, output, sep="");

	cat("\n<pre class=\"ROutput\">\n");
	for(i in seq_along(output)) {
		next.line <- output[i];
		while(next.line != strtrim(next.line, width = width + leading.spaces.num)) {
			str.to.cat <- strtrim(next.line, width = width - 6);
			cat(str.to.cat, "\n", sep="");
			next.line <- paste(continued.line.leading.spaces, substring(next.line, nchar(str.to.cat) + 1), sep="");
		}
		cat(next.line, "\n", sep="");
	}
	cat("</pre>\n");

}


web.table <- function(x, file.name="table.txt", before.link.text="Click ", link.text="here", after.link.text=" to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)", open.new.window=TRUE, attributes.text="", enclose.in.p = TRUE, ...) {
	sys.results.path <- (parent.env(environment())$WebDevelopR.vars)$full.sys.results.path
	web.results.path <- (parent.env(environment())$WebDevelopR.vars)$rel.web.results.path
	session.ID <- ((parent.env(environment())$WebDevelopR.vars)$form.data)$sessionID

	if(is.null(sys.results.path) || is.null(web.results.path)) {
		warning("Path to the results directory is not available.")
	} else {
		write.table(x, file=paste(sys.results.path, "session", session.ID, "-", file.name, sep=""), ...);
		if(open.new.window == TRUE) {
			attributes.text <- paste(attributes.text, "target=\"_blank\"");
		}
		if(enclose.in.p == TRUE) {
			before.link.text <- paste("<p>", before.link.text, sep="");
			after.link.text <- paste(after.link.text, "</p>", sep="");
		}
		cat(before.link.text, "<a href=\"", web.results.path, "session", session.ID, "-", file.name, "\" ", attributes.text, " >", link.text, "</a>", after.link.text, "\n", sep="");
	}
}


web.csv <- function(x, file.name="table.csv", before.link.text="Click ", link.text="here", after.link.text=" to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)", open.new.window=TRUE, attributes.text="", enclose.in.p = TRUE, ...) {
	sys.results.path <- (parent.env(environment())$WebDevelopR.vars)$full.sys.results.path
	web.results.path <- (parent.env(environment())$WebDevelopR.vars)$rel.web.results.path
	session.ID <- ((parent.env(environment())$WebDevelopR.vars)$form.data)$sessionID

	if(is.null(sys.results.path) || is.null(web.results.path)) {
		warning("Path to the results directory is not available.")
	} else {
		write.csv(x, file=paste(sys.results.path, "session", session.ID, "-", file.name, sep=""), ...);
		if(open.new.window == TRUE) {
			attributes.text <- paste(attributes.text, "target=\"_blank\"");
		}
		if(enclose.in.p == TRUE) {
			before.link.text <- paste("<p>", before.link.text, sep="");
			after.link.text <- paste(after.link.text, "</p>", sep="");
		}
		cat(before.link.text, "<a href=\"", web.results.path, "session", session.ID, "-", file.name, "\" ", attributes.text, " >", link.text, "</a>", after.link.text, "\n", sep="");
	}
}


web.csv2 <- function(x, file.name="table.csv", before.link.text="Click ", link.text="here", after.link.text=" to download your file.  (The link opens in a new window or tab; alternatively, you can right-click or option-click on the link and choose \"Save As...\" to download the file.)", open.new.window=TRUE, attributes.text="", enclose.in.p = TRUE, ...) {
	sys.results.path <- (parent.env(environment())$WebDevelopR.vars)$full.sys.results.path
	web.results.path <- (parent.env(environment())$WebDevelopR.vars)$rel.web.results.path
	session.ID <- ((parent.env(environment())$WebDevelopR.vars)$form.data)$sessionID

	if(is.null(sys.results.path) || is.null(web.results.path)) {
		warning("Path to the results directory is not available.")
	} else {
		write.csv2(x, file=paste(sys.results.path, "session", session.ID, "-", file.name, sep=""), ...);
		if(open.new.window == TRUE) {
			attributes.text <- paste(attributes.text, "target=\"_blank\"");
		}
		if(enclose.in.p == TRUE) {
			before.link.text <- paste("<p>", before.link.text, sep="");
			after.link.text <- paste(after.link.text, "</p>", sep="");
		}
		cat(before.link.text, "<a href=\"", web.results.path, "session", session.ID, "-", file.name, "\" ", attributes.text, " >", link.text, "</a>", after.link.text, "\n", sep="");
	}
}