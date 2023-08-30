import cv2
import numpy as np
import os
class Controller(object):
    def __init__(self,args):
        self.imgpth= args.input
        self.tmp = args.save_tmp
        self.imgPdir = args.imgPdir
        self.HoughCircleThd = args.lineEdit_4.text()
        self.HoughCircleminR = args.lineEdit_2.text()
        self.HoughCircleMaxR = args.lineEdit_3.text()
        self.image = cv2.imread(self.imgpth)
        self.grayimg = cv2.imread(self.imgpth,0)
        self.binimg = cv2.threshold(self.grayimg,127,255,cv2.THRESH_BINARY)
        self.gausimg = cv2.GaussianBlur(self.grayimg,(9,9),3)
        # self.dst = cv2.equalizeHist(self.gausimg)
        self.Canny = cv2.Canny(self.gausimg,30,100,apertureSize=3)
        Dkernel = np.ones((5,5),np.uint8)
        self.dildateCanny = cv2.dilate(self.Canny,kernel=Dkernel,iterations=1)
        

        if self.tmp:
            self.save_tmp()

    def save_tmp(self):
        srcimg = os.path.join(self.imgPdir,"srcimg.jpg")
        Cannyimg = os.path.join(self.imgPdir,"Canny,jpg")
        gausimg = os.path.join(self.imgPdir,"gausimg.jpg")
        cv2.imwrite(srcimg,self.image)
        cv2.imwrite(Cannyimg,self.Canny)
        cv2.imwrite(gausimg,self.gausimg)

class Sample(object):
    def __init__(self, args):
        self.imgpth = args.inputimage
        self.HoughCircleThd = args.lineEdit_4.text()
        self.HoughCircleminR = args.lineEdit_2.text()
        self.HoughCircleMaxR = args.lineEdit_3.text()
        self.image = cv2.imread(self.imgpth)
        self.grayimg = cv2.imread(self.imgpth, 0)
