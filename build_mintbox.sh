# nv:4oct2020
# This script builds the latest version of Astrobase as a Docker container
cd ~/my_docker/MyAstroBase
git pull
cd astrobase
sudo docker build -t my_astrobase:latest .
