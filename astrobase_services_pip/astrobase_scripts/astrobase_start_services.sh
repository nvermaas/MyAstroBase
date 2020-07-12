#!/bin/sh
# AstroBase script to start the 'background services'
# after pip install, start as production: nohup astrobase_start_services.sh &

# ingest looks for new images in the 'landing_pad' folder and moves them to 'raw' observations
astrobase_service -o ingest --interval 30 --astrobase_host http://uilennest.net/my_astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data -v &

# submits a new job and checks its progress
astrobase_service -o submit --interval 30 --astrobase_host http://uilennest.net/my_astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data --local_data_url http://uilennest.net/astrobase/data -v &

# processor submits a new job and handles the results
astrobase_service -o processor --interval 30 --astrobase_host http://uilennest.net/my_astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data --local_data_url http://uilennest.net/astrobase/data -v &

# remove data and database entries
astrobase_service -o cleanup --interval 60 --astrobase_host http://uilennest.net/my_astrobase --local_landing_pad ~/www/astrobase/landing_pad --local_data_dir ~/www/astrobase/data -v &
