#!/bin/bash
# ATTENTION: execute this script with sudo to not enter the password
while true
do
	docker-compose up -d web_scrapper
	echo "Running web_scrapper"
	echo "Start sleeping for 2 hours"
	sleep 7400
	docker-compose stop web_scrapper
	docker-compose rm -f web_scrapper
done