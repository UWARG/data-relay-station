#!/bin/sh

kill -9 $(ps x | grep [d]ata_relay.py | cut -d ' ' -f 2)
