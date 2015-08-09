#!/bin/bash



sqlite3 ./PTD1_BASA_CLD.GDB.sqlite  > info_ptd1_count_numissl_w_1024.txt <<!
select t.keyCNT,count(*) from (select count(*) as keyCNT from protocol where pngwidth > 1024 group by NUMBERKART having count(*)>1 order by count(*) desc) t group by t.keyCNT;
!


sqlite3 ./PTD2_BASA_CLD.GDB.sqlite  > info_ptd2_count_numissl_w_1024.txt <<!
select t.keyCNT,count(*) from (select count(*) as keyCNT from protocol where pngwidth > 1024 group by NUMBERKART having count(*)>1 order by count(*) desc) t group by t.keyCNT;
!
