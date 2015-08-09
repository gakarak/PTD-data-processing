#!/bin/bash

sqlite3 ./PTD2_BASA_CLD.GDB.sqlite <<!
alter table protocol add column ageissl;
update protocol set ageissl=(cast(substr(dateissl,7,4) as integer) - cast(substr(dateroshd,7,4) as integer));
!
