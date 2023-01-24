#!/bin/bash
while true
do
	echo "Running the code from shell script:"
	python3 bulk_manager.py
	python3 mg_web_main.py
	sleep 10
done