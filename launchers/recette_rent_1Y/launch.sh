#!/bin/bash

ROOT=/Users/alex/tri/distribs/bin

SELL=12

sed -i".bak" "s/infine=.*/infine=${SELL}/g" ${ROOT}/../etc/eco.properties

${ROOT}/rent.sh


 
