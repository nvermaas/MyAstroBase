#!/bin/sh
# AstroBase script to start the 'background services'
# after pip install, start as production: nohup astrobase_start_services.sh &

# data_monitor looks for new images in the 'landing_pad' folder and moves them to''raw' observations and its 'defined' dataproducts and puts them on 'completed'
astrobase_service -o data_monitor --interval 30 --astrobase_host http://192.168.178.62:8018/astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data -v &

# processor submits a new job and handles the results
astrobase_service -o processor --interval 30 --astrobase_host http://192.168.178.62:8018/astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data --local_data_url http://uilennest.net/astrobase/data -v &
