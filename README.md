# Rpi-Radio
Simple internet radio player for RaspberryPi 4 with web based GUI. Uses mplayer.

Tested on Pi 4B.

My intention was to publish a docker container for this project, but the process
of sharing a pulseaudio stream between the host and the container proved too
inconsistent across different distros.

# Usage (Linux)

Setup:
```
apt install mplayer
git clone https://github.com/nickpeck/rpi-radio.git
cd rpi-radio.ini.sample
cp rpi-radio.ini.sample rpi-radio.ini
python3 -m venv .
source bin/active
pip install -r requirements.txt
```

And then, to start:
```
export PYTHONPATH=${PYTHONPATH}:src
python3 -m rpiradio
```

visit http://{your hostname}:8080 to use the gui. User is 'admin' and the 
login password as defined in rpi-radio.ini
