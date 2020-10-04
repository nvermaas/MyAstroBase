# nv:4oct2020
# This script deploys the latest version of Astrobase
cd ~/my_docker/MyAstroBase
git pull
cd astrobase
sudo docker build -t my_astrobase:latest .
cd $HOME/shared
sudo docker-compose -p dockernest up -d