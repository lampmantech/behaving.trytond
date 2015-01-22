#!/bin/bash
# -*- encoding: utf-8  coding: utf8-unix -*-

# I know this is a groddy hack: fork me!

steps_to_txt () {
    local state=before
    local line
    
    cat $1 | \
    while read line ; do
	[ "$line" == "" ] && { continue ; }
	first=${line:0:1}
	if [ "$first" == "@" ] ; then
	    echo
            echo $line | sed -e "s/^@[a-z]*(u*[']/**/" -e "s/['])/**/"
	    state=before
	    continue
          fi
	sixth=${line:0:3}
	# shell strips the preceding whitespace on line
	if [ "$sixth" == '"""' ] ; then
	    if [ "$state" == "before" ] ; then
		state=in
	        continue
	      fi
	    if [ "$state" == "in" ] ; then
		state=outside
	        continue
	      fi
	  fi
	if [ "$state" == "in" ] ; then
	    echo "   $line"
	  fi
      done
}

find ../features/steps -type f -name \*.py | \
    grep -v '/support/\|__init__' | \
    while read file ; do
	outfile=`echo $file | sed -e 's@../features/steps/@@' -e 's@/@-@g' -e 's@py$@txt@'`
	steps_to_txt "$file" >> ${outfile}
	[ -s ${outfile} ] || { rm -f ${outfile} ; continue ; }
	echo -e "# -*- mode: text; fill-column: 75; coding: utf-8-unix; encoding: utf-8 -*-\n" > foo
	echo -e "From: $file\n\n" >> foo
	cat ${outfile} >> foo
	mv foo ${outfile}
      done
