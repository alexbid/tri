#!/bin/bash

ROOT=/Users/alex/tri/distribs/bin


SELL_BACK="12 24 36 48 60 72 84 96 108 120 144 156 240 360"

for SELL in ${SELL_BACK}
do

	# echo TUTU $
	# ls -l ${ROOT}/../etc/eco.properties
	sed -i".bak" "s/infine=.*/infine=${SELL}/g" ${ROOT}/../etc/eco.properties
	# grep infine ${ROOT}/../etc/eco.properties
	echo $SELL $(${ROOT}/buy.sh | grep NPV) $(${ROOT}/rent.sh | grep NPV)
done
