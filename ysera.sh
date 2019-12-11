#! /bin/bash
DIR=`dirname $0`

cd $DIR
source env/bin/activate
python ysera.py "$1"