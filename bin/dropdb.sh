#!/bin/sh
__doc__="
Scenario testing often requires a clean and empty database in Postgres.

This script will shut the trytond server down, drop the test database,
and then restart the server. Because it starts and stops the server,
it must be called as root. It assumes a sysv initscript in /etc/init.d

It is called with 3 arguments:
TRYTOND_VER - tryton version like 3.2
TUSER       - Unix user running the trytond daemon
dbname      - postgres database name you want to drop

"

if [ `id -u` -gt 0 ] ; then
    echo "ERROR: $0 must be run as root"
    exit 10
  fi

if [ "$#" -lt 3 -o "$1" = "--help" ] ; then
    echo "USAGE: $0 TRYTOND_VER TUSER dbname"
    echo $__doc__
    exit 11
  fi

TRYTOND_VER=$1
TUSER=$2
db=$3
PG_USER=postgres

#  2.4 2.6 2.8
for elt in $TRYTOND_VER ; do
    [ -x /etc/init.d/trytond-$elt ] || continue
    /etc/init.d/trytond-$elt status || continue
    /etc/init.d/trytond-$elt stop || { echo "ERROR: failed to stop $?" ; exit 12 ; }
  done
  
if su postgres -c "psql -l" | grep -q $TUSER ; then
	su postgres -c "psql -l" | grep $TUSER | while read a b c ; do \
	    [ -n "$a" ] || continue
	    echo "INFO: $TUSER database, have: $a looking for: ${db}"
	    [ "$a" = "${db}" ] || continue
	    echo "INFO: psql -c 'DROP DATABASE \"$a\";'"
	    su $PG_USER -c "psql -c 'DROP DATABASE \"$a\";'" \
	       2>&1| grep ERROR: && { echo "ERROR: failed to drop $a" ; exit 13 ; }
	  done
      fi

# sed -e "s@db_name = .*@db_name = ${db}@"  -i 
exit 0
