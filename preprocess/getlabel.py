import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import sys
import re
import cv2
import numpy as np
from PIL import Image
import easyocr
import pandas as pd

class getLabel(object):
    def __init__(self,obj):
        self.master = obj
        for key,val in vars(obj).items():
            setattr(self,key,val)

    def get_rectangle(self):
        '''
        Args:
        img:输入图片

        Return:
            图中的矩形框
        '''
        # img = cv2.imread(imgpth)
        # imgBlur = cv2.GaussianBlur(img,(13,13),3)
        # imgCanny = cv2.Canny(imgBlur,100,200)

        # kernel = np.ones((5,5),np.uint8)
        # imgDilate= cv2.dilate(imgCanny,kernel,iterations=1)
        # lines = cv2.HoughLinesP(image=imgDilate,rho=1,theta=np.pi/180,threshold=50,minLineLength=300)

        lines = cv2.HoughLinesP(image=self.dildateCanny,rho=1,theta=np.pi/180,threshold=50,minLineLength=300)
        if lines is None:
            print("未检测到标签！")
            self.croppedimg = self.image
            cv2.imwrite("cropped.jpg",self.image)
            return self.image
            # sys.exit()

        [xm,yM,xM,ym]=[[],[],[],[]]
        for i in range(len(lines)):
            line = lines[i][0]
            xm.append(line[0])
            yM.append(line[1])
            xM.append(line[2])
            ym.append(line[3])
            # [x1,y1,x2,y2] = lines[i][0]
            # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
        xmin,ymin,xmax,ymax = min(xm),min(ym),max(xM),max(yM)
        img= self.image
        cv2.rectangle(img,(xmin,ymax),(xmax,ymin),(0,255,0),2)

        srcimg = Image.open(self.imgpth)
        box = [xmin,ymin,xmax,ymax]
        roi = srcimg.crop(box)
        cv2.imwrite('rectangle.jpg',img)
        roi.save('cropped.jpg')
        self.croppedimg = cv2.imread('cropped.jpg',0)

        return img

    def get_note(self):
        '''
            用于获取图中的文字
        Args:
            img:输入图片

        Return:
            图中的文字
        '''
        reader = easyocr.Reader(['en'])
        ## 处理前，先截取图中标签段
        # if not hasattr(self,'croppedimg'):
        #     self.get_rectangle()
        # text = reader.readtext(self.croppedimg,detail=0)
        # 进行识别
        # text = reader.readtext(self.image,detail=0)
        # text = "".join(text).upper().replace(" ", "")

        #重整文字顺序
        text=reader.readtext(self.image,detail=1)
        sorted_data = sorted(text,key=lambda x:x[0][0])
        pdtext = pd.DataFrame(sorted_data)
        text = "".join(list(pdtext[1])).upper().replace(" ","_")
        text = re.sub(r'[^-0-9a-zA-Z]',"",text)
        self.imgname = text
        self.imgpth = "/".join(self.imgpth.split('/')[:-1])+"/"+ text + '.png'
        return text   
        
        
# if __name__ == "__main__":
#     reader = easyocr.Reader(['en'])
#     text = reader.readtext(r'D:\python_project\ColonyCounter-12-19\data\images\3\1\text\FXW-WM-E.png',detail=1)
#     sorted_data = sorted(text,key=lambda x:x[0][0])
#     text = pd.DataFrame(sorted_data)
#     atext = "".join(list(text[1])).upper().replace(" ","")
#     print(atext)
       
# def get_rectangle(imgpth):
#     '''
#     用于获取图中的矩形
#     Args:
#         img:输入图片

#     Return:
#         图中的矩形框
#     '''
#     img = cv2.imread(imgpth)
#     imgBlur = cv2.GaussianBlur(img,(13,13),3)
#     imgCanny = cv2.Canny(imgBlur,100,200)

#     kernel = np.ones((5,5),np.uint8)
#     imgDilate= cv2.dilate(imgCanny,kernel,iterations=1)
#     lines = cv2.HoughLinesP(image=imgDilate,rho=1,theta=np.pi/180,threshold=50,minLineLength=300)
#     cv2.imwrite('Canny.jpg',imgCanny)
#     [xm,yM,xM,ym]=[[],[],[],[]]
#     for i in range(len(lines)):
#         line = lines[i][0]
#         xm.append(line[0])
#         yM.append(line[1])
#         xM.append(line[2])
#         ym.append(line[3])
#         # [x1,y1,x2,y2] = lines[i][0]
#         # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
#     xmin,ymin,xmax,ymax = min(xm),min(ym),max(xM),max(yM)
#     cv2.rectangle(img,(xmin,ymax),(xmax,ymin),(0,255,0),2)

#     srcimg = Image.open(imgpth)
#     box = [xmin,ymin,xmax,ymax]
#     roi = srcimg.crop(box)
#     cv2.imwrite('rectangle.jpg',img)
#     roi.save('cropped.jpg')
#     return box

# def get_note(image):
#     '''
#         用于获取图中的文字
#     Args:
#         img:输入图片

#     Return:
#         图中的文字
#     '''
#     image = cv2.imread(image,0)
#     ret,img = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
#     cv2.imwrite('croppedCanny.jpg',img)
#     reader = easyocr.Reader(['en'])
#     text = reader.readtext(img,detail=0)
#     text = "".join(text).upper().replace(" ", "")
#     return text


# imgpth = 'square.jpg'
# # cv2.imshow('name1',img)
# box = get_rectangle(imgpth)
# cropped = 'cropped.jpg'

# print(get_note(cropped))