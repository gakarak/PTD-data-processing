#!/bin/bash

tptd="PTD1"

fdb="./${tptd}_BASA_CLD.GDB.sqlite"
fnumissl="lst_numissl_${tptd}.txt"

ftmp1="tmp_data_minnumissl_${tptd}.txt"
ftmp2="tmp_data_dateissl_${tptd}.txt"
ftmpSQL1="tmp_data_sql_minnumissl_${tptd}.sql"
ftmpSQL2="tmp_data_sql_dateissl_${tptd}.sql"


#########################################
### (1)
echo "::: ALTER AND CALC AGEISSL [$fdb]"
sqlite3 $fdb <<!
alter table protocol add column ageissl;
update protocol set ageissl=(cast(substr(dateissl,7,4) as integer) - cast(substr(dateroshd,7,4) as integer));
!

#########################################
### (2)
echo "::: CREATE NUMBERKART-INDEX {NUMBERKART_INDEX}"
sqlite3 $fdb <<!
create index NUMBERKART_INDEX on protocol (NUMBERKART);
!

#########################################
### (3)
echo "ALTER TABLE {NUMISSL} [$fdb]"
sqlite3 $fdb <<!
alter table protocol add column numissl;
!

echo "GET SET NUMISSL"

sqlite3 $fdb > "$fnumissl" <<!
select distinct count(*) from protocol where pngwidth > 0 group by NUMBERKART having count(*)>0 order by count(*) desc;
!

cat $fnumissl | while read ll
do
    echo "::: [$ll]"
sqlite3 $fdb <<!
    update protocol set numissl=${ll} where NUMBERKART in ( select NUMBERKART from protocol where pngwidth > 0 group by NUMBERKART having count(*)=${ll});
!
done

#########################################
### (4)
echo "::: PREPARE LIST {NUMBERKART,MIN-NUMBERISSL} [$ftmp1]"
sqlite3 $fdb > $ftmp1 <<!
--select NUMBERKART,DATEISSL,MIN(NUMBERISSL) from protocol group by NUMBERKART order by DATEISSL;
select NUMBERKART,MIN(NUMBERISSL) from protocol group by NUMBERKART;
!

### (4.1)
echo "::: GENERATE SQL FOR QUERY {NUMBERKART,MIN-NUMBERISSL} [$ftmpSQL1]"
cat $ftmp1 | sed 's/|/\ /g' | while read tval tpid
do
    echo "select NUMBERKART,DATEISSL from protocol where NUMBERKART=${tval} and NUMBERISSL=${tpid};"
done > $ftmpSQL1

echo "::: PREPARE LIST {NUMBERKART,DATEISSL} [$ftmp2]"
sqlite3 $fdb < $ftmpSQL1 > $ftmp2

echo "::: GENERATE SQL FOR UPDATE QUERY {NUMBERJART,DATEISSL} [$ftmpSQL2]"
cat $ftmp2 | sed 's/|/\ /g' | while read tval tpid
do
    echo "update protocol set dateisslfirst='${tpid}' where NUMBERKART='${tval}';"
done > $ftmpSQL2


### (4.2)
echo "::: ALTER TABLE {DATEISSLFIRST} [$fdb]"
sqlite3 ./$fdb <<!
alter table protocol add column dateisslfirst;
!

echo "::: UPDATE DB [$ftmpSQL2]"
sqlite3 $fdb < $ftmpSQL2

echo "::: ALTER AND CALC FIRST-AGEISSL [$fdb]"
sqlite3 ./$fdb <<!
alter table protocol add column ageisslfirst;
update protocol set ageisslfirst=(cast(substr(dateisslfirst,7,4) as integer) - cast(substr(dateroshd,7,4) as integer));
!
