#!/bin/bash
cmd=$(ebook-convert "$1" "$2".pdf --disable-font-rescaling --embed-all-fonts --level1-toc '//h:h1|//h:h2' --level2-toc '//h:h3' --level3-toc '//h:h4' --max-toc-links 0 --margin-bottom 1 --margin-top 1 --margin-right 1 --margin-left 1 --page-breaks-before '//h:hr')
