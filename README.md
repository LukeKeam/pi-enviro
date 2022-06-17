# easy install instructions 
curl -LJO https://raw.githubusercontent.com/LukeKeam/pi-enviro/master/install.sh && sudo sh ./install.sh

# notes
This script has enviro script which takes luftdaten_combined.py and puts all data into a sqlite db it also takes care of the setup of the db and stores all your data everytime it sends data to luftdaten <br/>
This assumes you are already installed and working with luftdaten_combined.py <br/>
All data is stored in /pi-enviro <br/>
Tested on a raspberry pi zero w

# Web-server available:
From http://IP:8050 for dashboard or if you changed your hostname to pi-enviro it can be http://pi-enviro:8050/

# get data, latest 20 records
cd /pi-enviro && sudo python3 db_get_records.py | head -20
# or more
cd /pi-enviro && sudo python3 db_get_records.py | more

# change lcd screen 
Hold your finger over the light sensor for 3secs. As this updates every 3 seconds

Please contribute :)

# Links
https://techgeek.biz/en/pi-enviro-dashboard-using-enviro/ <br/>
https://techgeek.biz/en/pi-enviro-dashboard-using-enviro/ <br/>
https://techgeek.biz <br/>
<br/>
https://github.com/pimoroni/enviroplus-python <br/>
https://learn.pimoroni.com/article/getting-started-with-enviro-plus#introduction for enviro+<br/>

# Luftdaten
https://learn.pimoroni.com/article/enviro-plus-and-luftdaten-air-quality-station#testing-the-luftdaten-script <br/>
https://devices.sensor.community/sensors 

# World Health Organisation links to some guidelins
https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines <br/>
https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health <br/>
https://www.who.int/publications/i/item/9789240034228 <br/>