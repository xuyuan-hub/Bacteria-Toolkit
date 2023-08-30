import cv2
import numpy as np
import os

class getCircle(object):
    
    def __init__(self,obj):
        for key,val in vars(obj).items():
            setattr(self,key,val)

    def getCircles(self):

        rows = self.grayimg.shape[0]
        gray = self.grayimg
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 2, rows / 2,
                                   param1=100, param2=int(self.HoughCircleThd),
                                   minRadius=int(self.HoughCircleminR), maxRadius=int(self.HoughCircleMaxR))
        self.flag = True if circles is not None else False
        if circles is not None:
            circles = np.uint16(np.around(circles))
            rows, cols = gray.shape
            img_circle = np.zeros((rows, cols, 1), np.uint8)
            img_circle[:, :, :] = 0  # 设置为全透明
            x = circles[0][0][0]
            y = circles[0][0][1]
            r = int(circles[0][0][2] * 0.95)
            img_circle = cv2.circle(img_circle, (x, y), r, (255), -1)
            # 直方图均衡化
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
            img_new = clahe.apply(gray)
            # 图片融合
            img_new = img_circle[:, :, 0] * img_new

            datafile = "/".join(self.imgpth.split('/')[:-1])
            self.file1 = self.imgpth.split('/')[-1]
            self.crop = datafile + "/crop"
            if (not os.path.exists(self.crop)):
                os.mkdir(self.crop)
            cv2.imwrite(self.crop + "/" + self.file1, img_new)

        # return img_new


def get_dish(img,circle_thd:int=200,min_r:int=200,max_r:int=800,):
    """
    detect whether img has a dish,if exists return cropped dish img, else return gray img
    :param img: cv2 img
    :param circle_thd: hough circle detect threshold
    :param min_r: hough circle minium radius
    :param max_r: hough circle max radius
    :return: [flag,cropped cv2 img]
    """
    gray_img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    rows = gray_img.shape[0]
    circles = cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 2, rows / 2,
                               param1=100, param2=circle_thd,
                               minRadius=min_r, maxRadius=max_r)
    flag = True if circles is not None else False
    if flag:
        circles = np.uint16(np.around(circles))
        rows, cols = gray_img.shape
        img_circle = np.zeros((rows, cols, 1), np.uint8)
        img_circle[:, :, :] = 0
        x = circles[0][0][0]
        y = circles[0][0][1]
        r = int(circles[0][0][2] * 0.95)
        img_circle = cv2.circle(img_circle, (x, y), r, (255), -1)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        img_new = clahe.apply(gray_img)
        # 图片融合
        img_new = img_circle[:, :, 0] * img_new

        return [flag,img_new]
    else:
        return [flag,gray_img]