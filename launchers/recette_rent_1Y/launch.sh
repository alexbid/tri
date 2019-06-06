#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

SELL=12
sed -i".bak" "s/infine=.*/infine=${SELL}/g" ${SCRIPTPATH}/../../distribs/etc/eco.properties

${SCRIPTPATH}/../../distribs/bin/rent.sh
#
