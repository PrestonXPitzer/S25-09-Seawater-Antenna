# S25-09 Seawater Antenna Controller Software

## Install
git clone this repo  
create and activate a local venv  
```
pip install -r requirements.txt
```

## Running
```
python3 antennaRunner.py
```

## Physical connections
connect physical pin 16 to DIR on H-Bridge  
connect physical pin 32 to PWM on H-Bridge  
connect physical pin 39 to relay GND  
connect physical pin 40 to relay 3.3_IN  
connect HDMI to display and usb to keyboard/mouse
