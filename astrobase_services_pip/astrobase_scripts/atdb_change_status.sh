#!/bin/sh
atdb_service -o change_status --resource observations --search_key taskid:$1 --status $2 --atdb_host prod -v
