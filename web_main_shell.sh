#!/bin/bash
while true
do
	echo "Running the code from shell script:"
	python3 -u mg_web_main.py
	python3 -u bulk_manager.py
	python3 -u mg_web_ibt_main.py
	sleep 10
done