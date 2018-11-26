-> location of systemd: 

/lib/system/system/picamera-oled.service

-> systemd data:

[Unit]
Description=PiCamera OLED Photo Booth

[Service]
Type=simple
Environment="DISPLAY=:0
ExecStart=/usr/bin/python3 -B /home/pi/picamera/video.py -d sh1106 -r 0 -i spi $

[Install]
WantedBy=graphical.target

