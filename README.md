# coop_weather_station
chicken coop weather station 

It has two BS18B20 temparature sensor, they are both attached at Pin5.

LED Pin2   : wifi status (green)
LED Pin 22 : data transfer (red)
LED Pin 23 : 2 probes found (yellow)

## useful commands

mpremote connect list  
mpremote connect [device name]
mpremote ls 

### copy files
mpremote cp main.py :main.py 

### reboot
mpremote connect /dev/cu.usbserial-0001 reset
mpremote connect /dev/cu.usbserial-0001 repl

