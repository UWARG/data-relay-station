# Base Station

This project contains the base station code for communicating with the aircraft.
It acts as an intermediary, collecting information from the data link (the xbee),
buffering the most recent telemetry blocks and sending them out to as many client
ground stations as desired.

## Architecture

```bash
# TODO: Make this diagram prettier

master ground station <=======IP/TCP====> base station <==XBEE==> plane
tertiary ground station <===|
tertiary ground station <===|
   .                        |
   .                        |
   .                        |
tertiary ground station <===/
```

## Install

Runs on Linux and Windows

Requires [python2.7](https://www.python.org/downloads/)

It is recommended to use [pip](http://pip.readthedocs.org/en/latest/installing.html)
to install the dependencies from the requirements.txt.
```
$ pip install -r requirements.txt
```

Probably even better to use virtualenv.

If you can't do that, you will need 
[Twisted](https://twistedmatrix.com/trac/wiki/Downloads),
[pySerial](https://pypi.python.org/pypi/pyserial),
[python-xbee](https://code.google.com/p/python-xbee/downloads/list)
and [argparse](https://docs.python.org/dev/library/argparse.html) (argparse is probably already installed
with python, but not always).
