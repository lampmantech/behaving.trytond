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

if su postgres -c "psql -l" | grep -q $TUSER ; then
	su postgres -c "psql -l" | grep $TUSER | while read a b c ; do \
	    [ -n "$a" ] || continue
	    echo "INFO: $TUSER database, have: $a looking for: ${db}"
	    [ "$a" = "${db}" ] || continue
	    /etc/init.d/trytond-$TRYTOND_VER status > /dev/null
	    retval=$?
	    # under Gentoo: 0=running 8=starting 3=stopped
	    if [ $retval -eq 0 -o $retval -eq 8 ]  ; then
		echo "INFO: dropdb.sh, stopping trytond-$TRYTOND"
		if /etc/init.d/trytond-$TRYTOND_VER stop 2>&1| \
		  grep ERROR: ; then
		    echo "ERROR: dropdb.sh, failed to stop $?"
		    exit 12
		fi
		sleep 10
	      fi
	    echo "INFO: psql -c 'DROP DATABASE \"$a\";'"
	    if su $PG_USER -c "psql -c 'DROP DATABASE \"$a\";'" \
		  2>&1| grep ERROR: ; then
		# psql returns 0 even on a failure
		echo "ERROR: dropdb.sh failed to drop $a"
		exit 13
	      fi
	  done
      fi

# sed -e "s@db_name = .*@db_name = ${db}@"  -i 
exit 0
