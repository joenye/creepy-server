#!/usr/bin/bash
while true
do
    if ! python tunnel.py; then
	exit
    fi
    sleep 0.2
done
