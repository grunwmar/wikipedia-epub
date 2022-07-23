#!/bin/bash
cmd=$(ebook-convert "$1" "$2".epub --flow-size 60 --disable-font-rescaling --embed-all-fonts --level1-toc '//h:h1|//h:h2' --level2-toc '//h:h3' --level3-toc '//h:h4' --epub-version 2 --max-toc-links 0 --margin-bottom 20 --margin-top 20 --margin-right 20 --margin-left 20 --page-breaks-before '//h:hr' --language "$3" --title "$4" --authors "Wikipedia.org - $6" --comments "$5")


