#!/bin/bash

set -e


export DIR=candidator
export VIRTUALENV=candidator-for-testing
export YAML_FILE_NAME="$1"

cd $DIR;
source $VIRTUALENV/bin/activate;

export YAML_FILE_NAME="$1";

if [ ! -e current_data.txt ]; then touch current_data.txt; fi

CURRENT_DATA=`cat current_data.txt`;

if [ "$CURRENT_DATA" != "$YAML_FILE_NAME" ]
then
	echo "$CURRENT_DATA y $YAML_FILE_NAME no son iguales";
	echo "$YAML_FILE_NAME" > current_data.txt;
	python manage.py reset_db --router=default --noinput;
	python manage.py syncdb --noinput;
	python manage.py loaddata $YAML_FILE_NAME;
	
else
	echo "$CURRENT_DATA y $YAML_FILE_NAME son iguales";
fi

 