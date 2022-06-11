# creat dir /pi-enviro
echo "make directory /pi-enviro "
mkdir /pi-enviro
cd /pi-enviro
# install git
sudo apt-get install git -y
# clone repository
echo "downloading update"
git clone https://github.com/LukeKeam/pi-enviro.git .
# make service so it starts automatically
echo "making service"
append_line='# sudo nano /lib/systemd/system/pi-enviro.service
# sudo systemctl restart pi-enviro.service
# sudo systemctl status pi-enviro.service
# sudo systemctl enable pi-enviro.service
# sudo systemctl daemon-reload
# User=pi?

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
# done
echo "all done"