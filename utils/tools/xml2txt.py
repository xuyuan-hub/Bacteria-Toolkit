import xml.etree.ElementTree as ET
import os

classes = ["dish"]
ValidList = ['png','tif','jpg']

def convert(size:list, box):
    """
    :param size:[width,height]
    :param box:
    :return:bounding box [x,y,w,h]
    """
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(xml_path:str,txt_path:str):
    """
    convert xml to txt
    :param img_path:path to input img
    :param xml_path:path to input xml
    :param txt_path:path to result txt
    :return:
    """
    with open(xml_path,'r') as f:
        root = ET.fromstring(f.read())
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    out_file = open(txt_path, 'w')
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in classes:
            print(cls)
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

def batch_process(dir_path:str):
    """
    convert all xml in dir_path to txt
    :param dir_path:
    :return:
    """
    for each_image in os.listdir(dir_path):
        image_name = os.path.basename(each_image)
        suffix = image_name.split('.')[-1]
        tidy_name = ".".join(image_name.split('.')[:-1])
        if suffix.lower() in ValidList:
            xml_path = os.path.join(dir_path,tidy_name+'.xml')
            txt_path = os.path.join(dir_path,tidy_name+'.txt')
            convert_annotation(xml_path=xml_path,txt_path=txt_path)

if __name__ == '__main__':
    dir_path = r'C:\Users\huihongyuan\PycharmProjects\BacteriaToolkit\ColonyCounter\data\images\dish\dish0818'
    batch_process(dir_path=dir_path)