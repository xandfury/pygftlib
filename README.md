[![Build Status](https://travis-ci.org/xandfury/pygftlib.svg?branch=master)](https://travis-ci.org/xandfury/pygftlib)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/764032d4494a4b8dbd6024419fc75e64)](https://www.codacy.com/app/xandfury/pygftlib?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=xandfury/pygftlib&amp;utm_campaign=Badge_Grade)

### Gevent based simple File Transfer Library

***Problem Statement***

> Two applications (written in python) - one reads a file and sends it over the network to the other application,
  which stores the file into its CWD. How would you do it (without using a framework that already does this)?
  L4 protocol of choice would be UDP, the reliability part is _your_ duty

***Solution***

Sender side is implemented as UDP clients via `gevent.sockets`, revceiver side is implemented using `gevent.server.DatagramServer`. I created 4 packet types on the top of UDP for TCP like features. This is to avoid data corruption of files due to problems relating to UDP. Essentially pygftlib introduces sequencing and acknowledgement mechanism to ensure reliability.

### Install
```
sudo -H python3 install setup.py
```


### Demo
```
$ pygftlib receive
                        __ _   _ _ _
 _ __  _   _  __ _ / _| |_| (_) |__
| '_ \| | | |/ _` | |_| __| | | '_ \
| |_) | |_| | (_| |  _| |_| | | |_) |
| .__/ \__, |\__, |_|  \__|_|_|_.__/
|_|    |___/ |___/

    Version:     0.1
    Module:      Receiver Module. Please use compatible client to connect with this!
    License:     MIT
    Credits:     Made by Abhinav Saxena <xandfury@gmail.com>.
                 Special thanks to Daniel Haslinger and Team Honeynet for letting me do this!

Starting Receiver/Server on 127.0.0.1:12345
[INFO:2018-04-08 23:15:08,719]:root: Starting Receiver/Server on 127.0.0.1:12345
New client has connected. Connection from 127.0.0.1:56270
[INFO:2018-04-08 23:15:37,463]:pygftlib.protocol: New client has connected. Connection from 127.0.0.1:56270
Creating new file with name: data.txt for client ('127.0.0.1', 56270)
[INFO:2018-04-08 23:15:37,464]:pygftlib.protocol: Creating new file with name: data.txt for client ('127.0.0.1', 56270)
File Transfer Complete! Wrote 2018-04-08 23:15:37 - data-txt to disk
[INFO:2018-04-08 23:15:38,475]:pygftlib.protocol: File Transfer Complete! Wrote 2018-04-08 23:15:37 - data-txt to disk
Removing client ('127.0.0.1', 56270) context. Either transfer has completed or client has been inactive for over 40 seconds
[INFO:2018-04-08 23:15:39,476]:pygftlib.protocol: Removing client ('127.0.0.1', 56270) context. Either transfer has completed or client has been inactive for over 40 seconds
New client has connected. Connection from 127.0.0.1:56270
[INFO:2018-04-08 23:15:39,477]:pygftlib.protocol: New client has connected. Connection from 127.0.0.1:56270
Invalid/Malformed INITRQ packet received from client ('127.0.0.1', 56270)
[WARNING:2018-04-08 23:15:39,479]:pygftlib.protocol: Invalid/Malformed INITRQ packet received from client ('127.0.0.1', 56270)

```
