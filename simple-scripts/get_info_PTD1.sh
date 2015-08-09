#!/bin/bash


sqlite3 ./PTD1_BASA_CLD.GDB.sqlite > info_ptd1.txt <<!
select ageissl,COUNT(*) from PROTOCOL where (ageissl>20 and ageissl<71 and (POL='ж' or POL='м') and pngwidth>1500 and opisanie<>'' AND expertsakl<>'') group by ageissl;
!