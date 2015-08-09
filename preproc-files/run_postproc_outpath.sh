#!/bin/bash

##tptd="PTD1"
tptd="PTD2"

fnumi="lst_numissl_${tptd}.txt"
fdb="${tptd}_BASA_CLD.GDB_age_num_first.sqlite"
diro="csv_by_numissl_${tptd}"

###################
if [ ! -f $fnumi ]; then
    echo "ERROR: cant find file [$fnumi]"
    exit 1
else
    echo "file [$fnumi] ... [ok]"
fi

###################
if [ ! -d "$diro" ]; then
    echo "cant find out-directory [$diro] ..."
    exit 1
fi

###################
cat $fnumi | while read ll
do
    finp="${diro}/exp_${ll}.csv"
    fout="${diro}/exp_${ll}.csv-path.txt"
    foutp="${diro}/exp_${ll}.csv-proc.csv"
    echo "--> [$finp]"
    echo "pathout" > $fout
    cat $finp | tail -n +2 | cut -d\| -f 2,3,4,5,10 | sed 's/|/\ /g'| while read tNumberkart tNumberIssl tPol tAgeIsslFirst tNumIssl
    do
##	tNumIssl=`echo "$ll" | cut -d\| -f 10`
##	tPol=`echo "$ll" | cut -d\| -f 4`
##	tAgeIsslFirst=`echo "$ll" | cut -d\| -f 5`
##	tNumberkart=`echo "$ll" | cut -d\| -f 2`
##	tNumberIssl=`echo "$ll" | cut -d\| -f 3`
	fpngOUT="${tNumIssl}/${tAgeIsslFirst}_${tPol}/${tNumberkart}/${tNumberkart}_${tNumberIssl}_orig.dcm.png"
	echo "$fpngOUT" >> $fout
    done
    echo "---> make [$foutp]"
    paste -d \| $finp $fout > $foutp
##    exit 1
done
