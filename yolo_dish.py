import shutil

import cv2
import os
import sys
import numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
import detect


def yolo_dish(img_path:str,wk_path:str):
    """
    use yolov5 to get picture's dish
    :param img_path:
    :param wk_path:
    :return: croped img_path
    """
    img = cv2.imread(img_path)
    opt = detect.parse_opt()
    opt.imgsz = [int(img.shape[1] / 32) * 32, int(img.shape[0] / 32) * 32]
    opt.project = wk_path
    opt.source = img_path
    opt.weights = os.path.join(ROOT, "weights", "yolo_dish.pt")
    detect.run(**vars(opt))

    img_name = os.path.basename(img_path)
    label_name = img_name.split('.')[0]+'.txt'
    label_path = os.path.join(wk_path,"exp","labels",label_name)
    if os.path.isfile(label_path):
        flag = True
        cropped_img = extract_dish(img_path,label_path)
    else:
        flag = False
        cropped_img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

    shutil.rmtree(os.path.join(wk_path,'exp'))
    return [flag,cropped_img]

def extract_dish(img_path:str,label_path:str):
    """

    :param img_path:
    :param location:
    :return: cropped img
    """
    img = cv2.imread(img_path)
    gray_img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    [height, width] = gray_img.shape
    locations = []
    with open(label_path,'r') as f:
        text = f.readlines()
        for line in text:
            location = line.split(" ")[1:]
            locations.append(location)

    dishes=[]
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    tmp_img = clahe.apply(gray_img)

    for i in range(len(locations)):
        location = locations[i]

        x = float(location[0])*width
        y = float(location[1])*height
        w = float(location[2])*width
        h = float(location[3])*height
        xmax = int((2 * x + w) / 2)
        ymax = int((2 * y + h) / 2)
        xmin = int((2 * x - w) / 2)
        ymin = int((2 * y - h) / 2)
        center_x = int((xmax+xmin)/2)
        center_y = int((ymax+ymin)/2)
        r = int(max((xmax-xmin)/2,(ymax-ymin)/2)*0.95)
        img_circle = np.zeros((height, width, 1), np.uint8)
        img_circle[:, :, :] = 0
        img_circle = cv2.circle(img_circle, (center_x, center_y), r, (255), -1)
        img_new = img_circle[:, :, 0] * tmp_img

        dishes.append(img_new)

    return dishes[0]
