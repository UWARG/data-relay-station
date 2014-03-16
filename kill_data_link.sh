#!/bin/sh

kill -9 $(ps x | grep '[p]ython data_relay.py' | cut -d ' ' -f 1)
kill -9 $(ps x | grep '[p]ython data_relay.py' | cut -d ' ' -f 2)
