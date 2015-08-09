#!/bin/bash

tptd="PTD1"
##tptd="PTD2"

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
    echo "make directory [$diro] ..."
    mkdir -p "$diro"
fi

###################
cat $fnumi | while read ll
do
    fout="${diro}/exp_${ll}.csv"
    echo "--> [$fout]"
sqlite3 $fdb <<!
.headers on
--.mode csv
.output ${fout}
select id,NUMBERKART,NUMBERISSL,POL,ageisslfirst,dateisslfirst,ageissl,DATEISSL,DATEROSHD,numissl,DIAGNOS,OPISANIE,pngwidth,pngheight,pngfilesize,pngfilepath
from protocol
where numissl=${ll}
order by ageisslfirst,POL,NUMBERKART,NUMBERISSL;
!
done
