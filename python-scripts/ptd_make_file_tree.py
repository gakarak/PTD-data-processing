#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'ar'

import sys
import os
import time
import shutil
import multiprocessing as mp
from multiprocessing import Value, Lock

tpdt='PTD2'
dirCFG="/home/ar/data/append_ageissl_numissl_firstissl_firstage_v2"
dirINP="/mnt/usb-Seagate_Expansion_Desk_NA4M4885-0:0-part1/"
dirOUT="/mnt/AE822A3E822A0B81/out_%s" % tpdt


def task_proc2(data):
    # print data
    finp=data[0]
    fout=data[1]
    # cntBEG=data[2]
    # cntEND=data[3]
    # tlock=data[4]
    # with tlock:
    #     cntBEG.value+=1
    deepCopy(finp, fout)
    # with tlock:
    #     cntEND.value+=1

class TaskManager:
    def __init__(self, nproc=4):
        self.nProc  = nproc
        self.pool   = mp.Pool(processes=self.nProc)
        self.cntTot = Value('i',0)
        self.cntEND = Value('i',0)
        self.cntBEG = Value('i',0)
        self.lock   = Lock()
    def appendTask(self, fpngINP, fpngOUT):
        # vdata=[fpngINP, fpngOUT, self.cntBEG, self.cntEND, self.lock]
        vdata=(fpngINP, fpngOUT)
        # with self.lock:
        #     self.cntTot.value+=1
        self.pool.apply_async(task_proc2, [vdata] )
    def printState(self):
        print("State: %d/%d/%d" % (self.cntTot.value, self.cntBEG.value, self.cntEND.value))

def readCSVData(winp, wout, fcsv):
    if not os.path.isfile(fcsv):
        print 'Cant find file [%s]' % fcsv
        sys.exit(1)
    lstLines=None
    with open(fcsv,'r') as f:
        lstLines=f.read().splitlines()[1:]
    ret=[]
    for ii in lstLines:
        tspl=ii.split('|')
        tfinp=tspl[-2].replace('\\','/')
        tfout=tspl[-1]
        tmp=(os.path.join(winp,tfinp), os.path.join(wout, tfout))
        ret.append(tmp)
    return ret

def deepCopy(finp, fout):
    if not os.path.isfile(finp):
        print 'ERROR: cant find file [%s]' % finp
        return
    if not os.path.isfile(fout):
        bdir=os.path.dirname(fout)
        if not os.path.isdir(bdir):
            os.makedirs(bdir)
        shutil.copy2(finp, fout)

def readLines(ftxt):
    with open(ftxt,'r') as f:
        return f.read().splitlines()

#############################
if __name__=='__main__':
    fcsvNumIssl=os.path.join(dirCFG, 'lst_numissl_%s.txt' % tpdt)
    if not os.path.isfile(fcsvNumIssl):
        print 'ERROR: cant find file [%s]' % fcsvNumIssl
        sys.exit(1)
    lstNUMISSL=readLines(fcsvNumIssl)
    for ii in lstNUMISSL:
        tii=int(ii)
        if tii>1:
            tfcsv="%s/csv_by_numissl_%s/exp_%d.csv-proc.csv" % (dirCFG, tpdt, tii)
            print ":: process [%s]" % tfcsv
            lst=readCSVData(dirINP, dirOUT, tfcsv)
            taskManager=TaskManager(nproc=8)
            for ii in lst:
                # print ii
                taskManager.appendTask(ii[0], ii[1])
            taskManager.pool.close()
            taskManager.pool.join()
