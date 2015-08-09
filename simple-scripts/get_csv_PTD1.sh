#!/bin/bash


sqlite3 ./PTD1_BASA_CLD.GDB.sqlite <<!
.headers on
.mode csv
.output data_ptd1.csv
select ageissl,POL,NUMBERKART,NUMBERISSL,pngfilepath,pngwidth,pngheight,opisanie,expertsakl from PROTOCOL where (ageissl>20 and ageissl<71 and (POL='ж'  or POL='м') and pngwidth>1500 and opisanie<>'' AND expertsakl<>'') order by ageissl,pol,NUMBERKART,NUMBERISSL;
!
