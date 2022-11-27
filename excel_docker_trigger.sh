#!/bin/bash
# ATTENTION: execute this script with sudo to not enter the password
while true
do
	echo "Running web_scrapper"
	docker-compose up excel_updater
	echo "Done web_scrapper"
	echo "Start sleeping for 24 hours"
	sleep 86400
	docker-compose stop excel_updater
	docker-compose rm -f excel_updater
done