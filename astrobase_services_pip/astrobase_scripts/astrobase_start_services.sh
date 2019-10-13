#!/bin/sh
# AstroBase script to start the 'background services'
# after pip install, start as production: nohup astrobase_start_services.sh &

# data_monitor looks for 'completed' observations and its 'defined' dataproducts and puts them on 'completed'
atdb_service -o data_monitor --interval 30 --atdb_host prod -v &

# start_ingest looks for 'valid' tasks and then starts the ingest to ALTA.
atdb_service -o start_ingest --interval 30 --atdb_host prod --alta_host prod -v &

# ingest_monitor looks if 'ingesting' tasks and dataproducts have arrived in ALTA, and when found sets their status in ATDB to 'archived'
atdb_service -o ingest_monitor --interval 30 --atdb_host prod --alta_host prod --user atdb --password V5Q3ZPnxm3uj -v &

# looks for 'archived' observations and deletes its 'archived' dataproducts
atdb_service -o cleanup --interval 60 --atdb_host prod -v &
