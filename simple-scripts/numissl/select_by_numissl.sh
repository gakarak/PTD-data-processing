#!/bin/bash



sqlite3 ./PTD1_BASA_CLD.GDB.sqlite <<!
select * from protocol  where NUMBERKART in (select NUMBERKART from protocol  group by NUMBERKART HAVING count(NUMBERKART) = 16);
!
