#!/bin/bash
echo "Thanks for choosing pi-enviro from techgeek.biz
This setup will take a while with the dashboard part"
# creat dir /pi-enviro
echo "make directory /pi-enviro "
mkdir /pi-enviro
cd /pi-enviro
sudo chown -R "$USER":"$USER" /pi-enviro
# install git
sudo apt-get update
sudo apt-get install git -y
# clone repository
echo "downloading update"
git clone https://github.com/LukeKeam/pi-enviro.git .
# make service so it starts automatically
echo "making service"
append_line='# pi-enviro systemctl file
[Unit]
Description=pi-enviro
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/pi-enviro
ExecStart=/bin/bash -c "python3 /pi-enviro/main.py"

[Install]
WantedBy=multi-user.target'
echo "$append_line" | sudo tee /lib/systemd/system/pi-enviro.service
sudo systemctl enable pi-enviro.service
sudo systemctl start pi-enviro.service
echo 'Starting pi-enviro! can take a 10mins to get stable readings'
# install python3 and venv and make venv
echo "Installing dashboard, this will take a few mins."
sudo apt-get install python3 python3-venv python-dev libatlas-base-dev -y
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt # dash==2.5.0 pandas==1.3.5 numpy==1.21.4 gunicorn==20.1.0 colorlover  # pre-compiled versions at https://piwheels.org/
sudo iptables -I INPUT -p tcp -m tcp --dport 8050 -j ACCEPT
# done
echo "all done!"
