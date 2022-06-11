This script has enviro script which takes luftdaten_combined.py and puts all data into a sqlite db it also takes care of the setup of the db and stores all your data everytime it sends data to luftdaten

This assumes you are already installed and working with luftdaten_combined.py

# easy install instructions 
curl -LJO https://raw.githubusercontent.com/LukeKeam/pi-enviro/master/install.sh && sudo sh ./install.sh

data is stored in /pi-enviro

# get data, latest 20 records
cd /pi-enviro && sudo python3 db_get_records.py | head -20


In the future could have this displayed on a local or remote webserver

Please contribute :)

Links
https://github.com/pimoroni/enviroplus-python
https://learn.pimoroni.com/article/getting-started-with-enviro-plus#introduction

Luftdaten
https://learn.pimoroni.com/article/enviro-plus-and-luftdaten-air-quality-station#testing-the-luftdaten-script
https://devices.sensor.community/sensors

World Health Organisation
https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines
https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health
https://www.who.int/publications/i/item/9789240034228