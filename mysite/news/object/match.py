import cv2
import matplotlib.pyplot as plt 
import time
import numpy as np

def getss(list):
    avg=sum(list)/len(list)
    ss=0
    for l in list:
        ss+=(l-avg)*(l-avg)/len(list)   
    return ss

def getdiff(img):
    avglist=[]
    try:
        Sidelength=30

        img=cv2.resize(img,(Sidelength,Sidelength),interpolation=cv2.INTER_CUBIC)
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        for i in range(Sidelength):
            avg=sum(gray[i])/len(gray[i])
            avglist.append(avg)
    except :
        print('error')
    return avglist

def getSim(img1, img2):
    if img1 is None or img2 is None:
        return 10000
    diff1=getdiff(img1)
    diff2=getdiff(img2)
    s = np.abs(getss(diff2)-getss(diff1))
    return s
