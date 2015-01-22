#!/bin/sh
# -*- encoding: utf-8 -*-
__doc__="
Quick and dirty hack to convert an Emacs buffer
of trytond doctest rst into behave feature file

Call it with 1 argument: rst-file-to-convert.rst
and it will convert it to rst-file-to-convert.feature
in the current directory.
"
[ "$#" -lt 1 ] && {
    echo "USAGE: $0 rst-file-to-convert"
    exit 1
}
[ "$1" = "--help" ] && {
    echo "USAGE: $0 rst-file-to-convert"
    echo $__doc__
    exit 0
}

base=`basename $1 .rst`
tofile="$base.feature"

cp -i "$1" "$tofile"

emacs -l rst_to_feature.el \
      --file "$tofile" \
      -f rst_to_feature \
      -f save-buffer -f save-buffers-kill-terminal
