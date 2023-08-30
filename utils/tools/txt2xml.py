import xml.etree.ElementTree as ET
import cv2
import pickle
import os
from os import listdir, getcwd
from os.path import join
import glob

classes = ["bacteria"]
wd = getcwd()
directory = 'D:\python_project\ColonyCounter-12-19\data\images/2023-03-07/train'

# def convert(size, box):
#     dw = 1.0 / size[0]
#     x = (box[0] + box[1]) / 2.0
#     y = (box[2] + box[3]) / 2.0
#     w = box[1] - box[0]
#     h = box[3] - box[2]
#     x = x * dw
#     w = w * dw
#     y = y * dh
#     h = h * dh
#     return (x, y, w, h)


def convert_annotation(image_path):
    image_name = image_path.split('\\')[-1]
    out_file = directory+'/' + image_name[:-4] + '.xml' # xml文件路径
    in_file = open(directory+'/' + image_name[:-3] + 'txt', 'r')  # 转换后的txt文件存放路径
    # f = open(in_file)

    #获得图片的尺寸
    img1 = cv2.imread(image_path,0)
    [height, width] = img1.shape

    tree = ET.Element("annotation")
    t_folder = ET.SubElement(tree, 'folder')
    t_fname = ET.SubElement(tree, 'filename')
    t_path = ET.SubElement(tree, 'path')
    t_source = ET.SubElement(tree, 'source')
    t_size = ET.SubElement(tree,'size')
    t_seg = ET.SubElement(tree,'segmented')
    t_folder.text = 'annotations'
    t_fname.text = image_name
    t_path.text = image_path
    t_db = ET.SubElement(t_source,'database')
    t_db.text = 'Unknown'
    t_seg.text = str(0)
    t_width = ET.SubElement(t_size,'width')
    t_height = ET.SubElement(t_size,'height')
    t_depth = ET.SubElement(t_size,'depth')
    t_width.text = str(width)
    t_height.text = str(height)
    t_depth.text = str(1)
    yolo_text = in_file.readlines()
    for line in yolo_text:
        bacteria = ET.SubElement(tree,'object')
        t_name = ET.SubElement(bacteria,'name')
        t_pose = ET.SubElement(bacteria,'pose')
        t_truc = ET.SubElement(bacteria,'truncated')
        t_diff = ET.SubElement(bacteria,'difficult')
        t_bndx = ET.SubElement(bacteria,'bndbox')
        t_name.text = 'bacteria'
        t_pose.text = 'Unspecified'
        t_truc.text = str(0)
        t_diff.text = str(0)
        bndx_xm = ET.SubElement(t_bndx,'xmin')
        bndx_ym = ET.SubElement(t_bndx,'ymin')
        bndx_xM = ET.SubElement(t_bndx,'xmax')
        bndx_yM = ET.SubElement(t_bndx,'ymax')
        x = float(line.split(' ')[1]) * width
        y = float(line.split(' ')[2]) * height
        w = float(line.split(' ')[3]) * width
        h = float(line.split(' ')[4].strip()) * height
        xmax = int((2*x+w)/2)
        ymax = int((2*y+h)/2)
        xmin = int((2*x-w)/2)
        ymin = int((2*y-h)/2)
        bndx_xm.text,bndx_ym.text,bndx_xM.text,bndx_yM.text = str(xmin),str(ymin),str(xmax),str(ymax)
    trees = ET.ElementTree(tree)
    trees.write(out_file)



if __name__ == '__main__':

    for image_path in glob.glob(directory+"/*.Tif"):  # 每一张图片都对应一个xml文件这里写xml对应的图片的路径
        convert_annotation(image_path)
    for image_path in glob.glob(directory+"/*.png"):  # 每一张图片都对应一个xml文件这里写xml对应的图片的路径
        convert_annotation(image_path)