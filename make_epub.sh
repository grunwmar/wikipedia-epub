#!/bin/bash

cov_=$(python3 make_envelope.py "$4" "$6" "$3")

COVERSVG="$PWD/tmp/envelope_$4_svg.svg"
COVERPNG="$PWD/tmp/envelope_$4_svg.png"

#cmd1=$(convert -density 256 "$COVERSVG" "$COVERPNG")
cmd1=$(inkscape --export-background-opacity=0 --export-type=png --export-filename="$COVERPNG" "$COVERSVG")



cmd2=$(ebook-convert "$1" "$2".epub --flow-size 60 --disable-font-rescaling --embed-all-fonts --level1-toc '//h:h1|//h:h2' --level2-toc '//h:h3' --level3-toc '//h:h4' --epub-version 2 --max-toc-links 0 --margin-bottom 20 --margin-top 20 --margin-right 20 --margin-left 20 --page-breaks-before '//h:hr' --language "$3" --title "$4" --authors "Wikipedia.org - $6" --comments "$5" --cover "$COVERPNG")

#cmd=$(pandoc -f html -t epub3 -o "$2".epub "$1")
