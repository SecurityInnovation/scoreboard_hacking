# Scoreboard Hacker

Ever thought of trying to change the score or modify the time on a scoreboard? Us too!   
This project is a result of Jesse Victors and Maxwell Dulin's research into scoreboards.   
This repository holds the code used throughout this project to control the scoreboard, run tests and a multitude of other things. The assets are listed below.

For more information on all of this, please check out the blog posts at 
- Introduction & Signal Analysis - [Part 1](https://maxwelldulin.com/BlogPost/Scoreboard-Hacking-Signal-Analysis-Part-1)
- Stealing the AES Key & Other Settings via Hardware Hacking - [Part 2](https://maxwelldulin.com/BlogPost/Scoreboard-Hacking-Part-2)
- Full Protocol replication in Python and GNU Radio - [Part 3](https://maxwelldulin.com/BlogPost/Scoreboard-Hacking-Part-3)

## Calling
- Pre Reqs: 
    - SDR capable of transmitting data. Currently, the gnu radio code is configured for a HackRF One or HackRF Jawbreaker, but this could be easily changed with small modifications to the sync of the flow graph. 
    - GNU Radio compatiable system with the version of the GNU radio that was used. We used the [GNU Radio Linux distro](https://www.gnuradio.org/blog/2016-05-28-using-gnu-radio-live-sdr-environment/) for this but this isn't a requirement. 
    - Python3 libraries: 
        - ``crcmod`` 
        - The python3 crypto library
    - Known baud rate of the scoreboard device. We purposely make you set this in order to prevent script kiddies from trivally using this without knowing what is going on. Our thought is that somebody who could figure this parameter out could build their own controller anyway. 

- Starting the program:
```
python3 ./controller.py <baud rate>
```
- This pulls up a menu. Now, you can do whatever your heart desires :) 

## controller.py 
- The link between all of the code.
- Has a command line interface (CLI) to arbitrary edit the scoreboard. 
- Calls ``packet.py`` to create the data to send. Calls ``modem.py`` to edit the content being sent. 

## modem.py 
- The GNU radio Python code output from GNU radio companion with slight changes. 
- Creates the *frequency shift keying* (FSK) code and sends the data to the SDR.  

## Packet.py 
- Creates the full packet for the transmitter. 
- This includes the AES encryption, CRC and many other things. ``scoreboard.py`` is used by this. 

## scoreboard.py 
- Handles the state and changes made to the scoreboard itself. Has the game clock, scores, fouls and everything else pertaining to the scoreboard. 

## lfsr.py 
- The utils for performing all of the operations. 
- Contains the AES encryption, data whitening, intiailization value brute forcing and CRC low level code. 

## compare.py 
- Several tests we ran while trying to figure out the packet format. Not super useful anymore but was important for the reverse engineering process. 
