#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'ar'

import math
import time
import os
import sys
import numpy as np
import cv2
from skimage import io
import skimage.filters
import sklearn.metrics as MT
import shutil
import multiprocessing as mp

import pandas as pd

import matplotlib.pyplot as plt

#################################
def task_proc_segmxr3(data):
    ptrPathWdir     = data[0]
    ptrPathImg      = data[1]
    regXR           = RegisterXray()
    pathImgMask     = "%s_proc_mask.png"   % ptrPathImg
    pathImgMasked   = "%s_proc_masked.png" % ptrPathImg
    pathImgOnMask   = "%s_proc_onmask.png" % ptrPathImg
    pathPtsCSV      = "%s_proc_pts.csv"    % ptrPathImg
    #
    if os.path.isfile(pathImgMasked):
        print "skip file [%s] ..." % ptrPathImg
        return
    if not os.path.isfile(ptrPathImg):
        print "cant find file [%s] ..." % ptrPathImg
        return
    #
    regXR.loadDB(ptrPathWdir)
    # regXR.printInfo()
    retMsk,retCorr,sumPts,ptsXY  = regXR.registerMask(ptrPathImg, isRemoveDir=True)
    if retCorr>regXR.threshCorrSum:
        cv2.imwrite(pathImgMask,   regXR.newMsk)
        cv2.imwrite(pathImgMasked, regXR.newImgMsk)
        # cv2.imwrite(pathImgOnMask, regXR.newImgOnMsk)
        np.savetxt(pathPtsCSV, regXR.pts, delimiter=',', newline='\n', fmt='%0.1f')
    else:
        tmpNewImgMsk = cv2.imread(ptrPathImg, 1) #cv2.IMREAD_COLOR)
        tmpImgOnMsk  = np.zeros((tmpNewImgMsk.shape[0],tmpNewImgMsk.shape[1]), np.uint8)
        p00=(0,0)
        p01=(0,tmpNewImgMsk.shape[0])
        p10=(tmpNewImgMsk.shape[1],0)
        p11=(tmpNewImgMsk.shape[1], tmpNewImgMsk.shape[0])
        cv2.line(tmpNewImgMsk, p00, p11, (0,0,255), 4)
        cv2.line(tmpNewImgMsk, p01, p10, (0,0,255), 4)
        regXR.newMsk[:]=0
        cv2.imwrite(pathImgMask,   regXR.newMsk)
        cv2.imwrite(pathImgMasked, tmpNewImgMsk)
        # cv2.imwrite(pathImgOnMask, tmpImgOnMsk )
        # tmpPts=np.zeros((7,2), np.float64)
        # np.savetxt(tmpPts, delimiter=',', newline='\n')
        fnErr="%s_proc.err" % ptrPathImg
        f=open(fnErr,'w')
        f.close()

class TaskManagerSegmXR:
    def __init__(self, nproc=8):
        self.nProc  = nproc
        self.pool   = mp.Pool(processes=self.nProc)
        self.regXR = RegisterXray()
    def loadData(self, wdir):
        if not os.path.isdir(wdir):
            print "ERROR-LOAD-XRAY-DB: Can't find directory [%s]" % wdir
            return False
        self.wdir = wdir
        ret=self.regXR.loadDB(wdir)
        self.regXR.printInfo()
        return ret
    def appendTaskSegmXR(self, fimg):
        vdata=[self.wdir, fimg]
        # self.pool.apply_async(task_proc_segmxr, [vdata] )
        self.pool.apply_async(task_proc_segmxr3, [vdata] )

#################################
class RegisterXray:
    def __init__(self):
        self.numNGBH=5
        self.siz=256
        self.wsiz=(self.siz, self.siz)
        self.fnDscShort="dsc.csv"
        self.fnIdxShort="idx.csv"
        self.fnParamShort="parameters_BSpline.txt"
        ##self.run_elastix="elastix -f %s -m %s -p %s -out %s -threads 4 >/dev/null"
        self.run_elastix="elastix -f %s -m %s -p %s -out %s -threads 4 >/dev/null"
        self.run_transformix="transformix -in %s -tp %s/TransformParameters.0.txt -out %s >/dev/null"
        self.fnResImgShort="result.0.bmp"
        self.fnResMskShort="result.bmp"
        self.newMsk=None
        self.newImgMsk=None
        self.pts=None
        self.newImgOnMsk=None
        self.threshCorrSum = 0.5
    def loadDB(self, parDirDB):
        self.wdir = parDirDB
        if not os.path.isdir:
            print "Can't find directory [%s]" % self.wdir
            return False
        self.odir = "%s-out" % self.wdir
        try:
            os.mkdir(self.odir)
        except:
            pass
        if not os.path.isdir(self.odir):
            print "Can't create out-directory [%s]" % self.odir
            return False
        tmpFnDscFull="%s/%s" % (self.wdir, self.fnDscShort)
        tmpFnIdxFull="%s/%s" % (self.wdir, self.fnIdxShort)
        tmpFnParamFull="%s/%s" % (self.wdir, self.fnParamShort)
        if not os.path.isfile(tmpFnDscFull):
            print "Ca't find DSC-file in DB [%s]" % tmpFnDscFull
            return False
        if not os.path.isfile(tmpFnIdxFull):
            print "Can't find Index-file in DB [%s]" % tmpFnIdxFull
            return False
        if not os.path.isfile(tmpFnParamFull):
            print "Can't find Elastix-Param-file in DB [%s]" % tmpFnParamFull
            return False
        self.fnDsc=tmpFnDscFull
        self.fnIdx=tmpFnIdxFull
        self.fnParam=tmpFnParamFull
        self.dataDsc=np.genfromtxt(self.fnDsc, delimiter=',')
        self.dataIdx=self.getLines(self.fnIdx)
        self.dataFnImg=[]
        self.dataFnMsk=[]
        for idx in self.dataIdx:
            tmpfImg='%s/%s.png' % (self.wdir, idx)
            tmpfMsk='%s/%s.bmp' % (self.wdir, idx)
            if not os.path.isfile(tmpfImg):
                print "Error: Can't find Image-file in DB [%s]" % tmpfImg
                return False
            if not os.path.isfile(tmpfMsk):
                print "Error: Can't find Mask-file in DB [%s]" % tmpfMsk
                return False
            self.dataFnImg.append(tmpfImg)
            self.dataFnMsk.append(tmpfMsk)
        if len(self.dataIdx)!=len(self.dataDsc):
            print "Error: Incorrect Index or DSC data"
            return False
        return True
    """
    Adjust image brightness by percentile
    """
    def adjustImage(self, img, perc):
        im = img.astype(np.float)
        tbrd=int(math.floor(0.1*np.min(im.shape)))
        imc=im[tbrd:-tbrd, tbrd:-tbrd]
        q0, q1 = np.percentile(imc[:], [perc, 100.0-perc])
        imm=np.max(im[:])
        im=255.*(im-q0)/( (2.0*perc*imm/100.) + q1-q0)
        im[im<0]=0
        im[im>255]=255
        return im
    def calcDscRadon(self, img):
        if len(img.shape)!=2:
            print "Error: bad image format: ", img.shape
            return None
        dsc=np.concatenate((np.sum(img,axis=0), np.sum(img,axis=1)))
        dsc=dsc/(img.shape[0]*img.shape[1])
        return dsc
    def getOutDir(self):
        return "%s/out-%d" % (self.odir, time.time()*1000)
    def helperMkDir(self, dirName):
        try:
            os.mkdir(dirName)
        except:
            pass
        if not os.path.isdir(dirName):
            print "Error: Can't create directory [%s]" % dirName
            return False
        else:
            return True
    def findNGBH(self, img):
        dsc=self.calcDscRadon(img)
        tdst=MT.pairwise_distances(self.dataDsc, [dsc], metric='correlation')[:,0]
        sidx=np.argsort(tdst)[:self.numNGBH]
        return sidx
    """
    Main function: return registered mask
    """
    def registerMask(self, fimg, isRemoveDir=False, fmsk=None):
        # img=cv2.imread(fimg, cv2.IMREAD_GRAYSCALE).astype(np.float64)
        img=cv2.imread(fimg, 0).astype(np.float64)
        siz0=img.shape
        img=cv2.resize(img, self.wsiz)
        img=self.adjustImage(img, 1.0)
        retNgbh=self.findNGBH(img)
        tdirOut=self.getOutDir()
        self.helperMkDir(tdirOut)
        toutMsk="%s/%s" % (tdirOut, self.fnResMskShort)
        toutImg="%s/%s" % (tdirOut, self.fnResImgShort)
        tfin="%s/fix.png" % tdirOut
        cv2.imwrite(tfin, np.uint8(img))
        sumMask=None
        sumPts =None
        sumCorr=0.0
        maxCorr=-100
        for ii in retNgbh:
            # print "prcess %d : %s" % (ii, self.dataFnImg[ii])
            tfmovImg=self.dataFnImg[ii]
            tfmovMsk=self.dataFnMsk[ii]
            tfmovPts='%s_pts.png' % tfmovImg
            strRun0=self.run_elastix     % (tfin, tfmovImg, self.fnParam, tdirOut)
            strRun1=self.run_transformix % (tfmovMsk, tdirOut, tdirOut)
            os.system(strRun0)
            os.system(strRun1)
            # tmsk=cv2.imread(toutMsk, cv2.IMREAD_GRAYSCALE).astype(np.float)/255.0
            tmsk=cv2.imread(toutMsk, 0).astype(np.float)/255.0
            tmsk=skimage.filters.gaussian(tmsk, 0.5)
            # timg=cv2.imread(toutImg, cv2.IMREAD_GRAYSCALE).astype(np.float)
            timg=cv2.imread(toutImg, 0).astype(np.float)
            curCorr=np.corrcoef(img[20:-20].reshape(-1), timg[20:-20].reshape(-1))[0,1]
            sumCorr+=curCorr
            if sumMask is None:
                sumMask=tmsk
            else:
                sumMask+=tmsk
            #### PTS
            strRun2=self.run_transformix % (tfmovPts, tdirOut, tdirOut)
            os.system(strRun2)
            tpts=cv2.imread(toutMsk, 0)
            if maxCorr<curCorr:
                sumPts=tpts.copy()
                maxCorr=curCorr
        ### PTS-array (prepare)
        sumCorr/=self.numNGBH
        ret=(sumMask/self.numNGBH)
        ret=cv2.resize(ret,(siz0[1],siz0[0]), interpolation=2)
        ret=(ret>0.5)
        ret=255*np.uint8(ret)
        numPts=7
        ptsXY=np.zeros((numPts,2), np.float64)
        kxy=(ret.shape[1]/256., ret.shape[0]/256.)
        for pp in xrange(0,7):
            pvalue=100+20*pp
            xy=np.where(sumPts==pvalue)
            if len(xy[0])>0:
                xym=np.mean(xy,1)
                ptsXY[pp,0]=xym[1]*kxy[0]
                ptsXY[pp,1]=xym[0]*kxy[1]
            else:
                ptsXY[pp,0]=-1.0
                ptsXY[pp,1]=-1.0
        if isRemoveDir:
            shutil.rmtree(tdirOut)
        self.newMsk=ret
        self.pts=ptsXY.copy()
        self.newImgMsk=self.makeMaskedImage(fimg, self.newMsk)
        self.newImgOnMsk=self.makeImgOnMask(fimg, self.newMsk)
        return (ret,sumCorr,sumPts,ptsXY)
    def makeMaskedImage(self, fimg, msk):
        img=cv2.imread(fimg, 1) #cv2.IMREAD_COLOR)
        tmp=img[:,:,2]
        tmp[msk>0]=255
        img[:,:,2]=tmp
        if self.pts is not None:
            numPts=self.pts.shape[0]
            scaleSiz=np.min( (img.shape[0],img.shape[1]) )
            prad=int(5.*scaleSiz/256.)
            for pp in xrange(0,numPts):
                cpp=self.pts[pp]
                cv2.circle(img, (int(cpp[0]), int(cpp[1])), prad+2, (255,255,255), -1) # cv2.cv.FILLED
                cv2.circle(img, (int(cpp[0]), int(cpp[1])), prad+0, (0,0,255), -1) # cv2.cv.FILLED
        return img
    def makeImgOnMask(self, fimg, msk):
        tmpImg=cv2.imread(fimg, 0).astype(np.int32)
        tmpImg=tmpImg+1
        tmpImg[tmpImg>255]=255
        tmpImg[msk==0]=0
        tmpImg=tmpImg.astype(np.uint8)
        return tmpImg
    def printInfo(self):
        print "-- Info --"
        print "Wdir:    ", self.wdir
        print "Dsc:     ", self.fnDsc
        print "Idx:     ", self.fnIdx
        print "Params:  ", self.fnParam
        print "DB-Size: ", len(self.dataIdx)
        print "*RUN[elatix]:      ", self.run_elastix
        print "*RUN[transformix]: ", self.run_transformix
    def getLines(self, fname):
        ret=None
        with open(fname,'r') as f:
            ret=f.read().splitlines()
        return ret

#################################
def test_main():
    def_wdir='/home/ar/github.com/PTD-data-processing.git/data/datadb.segmxr'
    lst_fimg=('/home/ar/github.com/PTD-data-processing.git/data/test_xrsegm/46106_10_orig.dcm.png_r512.png2',
              '/home/ar/github.com/PTD-data-processing.git/data/test_xrsegm/486455_100_orig.dcm.png_r512.png2',
              '/home/ar/github.com/PTD-data-processing.git/data/test_xrsegm/lena.jpg')
    for ii in lst_fimg:
        task_proc_segmxr3((def_wdir, ii))

#################################
if __name__=="__main__":
##    test_main()

##    sys.exit(1)
    if len(sys.argv)<3:
        print "Usage: %s {/path/to/xray-DB} {/path/to/file-list.csv}" % os.path.basename(sys.argv[0])
        sys.exit(1)
    dirXrayDB=sys.argv[1]
    fnCSV=sys.argv[2]
    def_wdir=dirXrayDB #'/home/ar/work/work.webcrdf/data/datadb.segmxr'
    if not os.path.isfile(fnCSV):
        print "Can't find CSV-file [%s]" % fnCSV
        sys.exit(1)
    taskManager = TaskManagerSegmXR(6)
    retLoadDB = taskManager.loadData(def_wdir)
    if not retLoadDB:
        print "ERROR: Can't load Xray-DB [%s], exit... " % dirXrayDB
        sys.exit(2)
    #
    lst_fimg = pd.read_csv(fnCSV, header=None)[0].as_matrix()
    lst_fimg = np.array([os.path.join(os.path.dirname(fnCSV), xx) for xx in lst_fimg])

    # f=open(fnCSV)
    # lst_fimg=f.readlines()
    # f.close()
    if len(lst_fimg)<1:
        print "Error: bad CSV file [%s]" % fnCSV
        sys.exit(3)
    # sys.exit(0)
    ##os.system("taskset -p 0xff %d" % os.getpid())
    for ff in lst_fimg:
        tfn = ff.strip()
        print "append task [%s]" % tfn
        taskManager.appendTaskSegmXR(tfn)
        time.sleep(0.002)
    taskManager.pool.close()
    taskManager.pool.join()
