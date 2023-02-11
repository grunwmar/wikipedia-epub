#!/bin/bash
cmd=$(ebook-convert "$1" "$2".pdf --disable-font-rescaling --embed-all-fonts --level1-toc '//h:h1|//h:h2' --level2-toc '//h:h3' --level3-toc '//h:h4' --max-toc-links 0 --page-breaks-before '//h:hr' --language "$3" --title "$4" --authors "Wikipedia.org - $6" --comments "$5" --pdf-page-margin-bottom 30 --pdf-page-margin-top 30 --pdf-page-margin-left 30 --pdf-page-margin-right 30)
