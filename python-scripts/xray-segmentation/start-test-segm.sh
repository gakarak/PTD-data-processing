#!/bin/bash

runpy="proc_algsegm_xray.py"

pathDB="../../data/datadb.segmxr"
pathTest="../../data/test_xrsegm/idx.txt"

python ${runpy} ${pathDB} ${pathTest}

