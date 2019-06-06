#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

SELL_BACK="12 24 36 48 60 72 84 96 108 120 144 156 168 180 192 204 216 228 240 360"

echo HOLDING_PERIOD NPV_BUY NPV_RENT

for SELL in ${SELL_BACK}
do

	# echo TUTU $
	# ls -l ${ROOT}/../etc/eco.properties
	sed -i".bak" "s/infine=.*/infine=${SELL}/g" ${SCRIPTPATH}/../../distribs/etc/eco.properties
	# grep infine ${ROOT}/../etc/eco.properties
	echo $SELL $(${SCRIPTPATH}/../../distribs/bin/buy.sh | grep NPV) $(${SCRIPTPATH}/../../distribs/bin/rent.sh | grep NPV)
done
#
