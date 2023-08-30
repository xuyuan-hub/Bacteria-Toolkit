import logging
import os
import sys
import cv2
import shutil
import datetime
from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog
from PyQt5.QtCore import pyqtSignal,QTimer,QThread
from PyQt5 import QtGui

ROOT = os.path.dirname(os.path.abspath(__file__))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from GUI.BacteriaToolkit import Ui_mainWindow as ToolkitUi
import detect
from preprocess.get_circle import get_dish
from yolo_dish import yolo_dish

class DetectThread(QThread):
    work_finished = pyqtSignal(object)  # 自定义信号，用于通知主线程转换完成

    def __init__(self, work):
        self.work = work
        super(DetectThread, self).__init__()

    def run(self):
        result = self.work
        self.work_finished.emit(result)  # 发送转换完成信号

class QTextEditHandler(logging.Handler):
    def __init__(self, text_edit):
        super(QTextEditHandler, self).__init__()
        self.text_edit = text_edit
        self.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)
        QApplication.processEvents()

class myMainWindow(ToolkitUi,QMainWindow):
    _signal = pyqtSignal

    def __init__(self):

        super(ToolkitUi,self).__init__()
        self.setupUi(self)
        self.timer = QTimer(self)
        self._init_logger()
        self.slot_init()
        self.display_size = self.imageLabel.size()
        self.csv_pairs = []
        self.valid_images_format = ['jpg', 'tif', 'png', 'jpeg']

    def slot_init(self):
        self.openImageButton.clicked.connect(self.choose_image)
        self.openImageDirButton.clicked.connect(self.open_directory)
        self.LaunchButton.clicked.connect(self.detect)

    def _init_logger(self):
        self.LOGGER = logging.Logger("Bacteria Toolkit Logger")
        self.LOGGER.setLevel(logging.DEBUG)
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        self.run_path = os.path.join(ROOT, "run", formatted_datetime)
        text_edit_handler = QTextEditHandler(self.textBrowser)
        self.LOGGER.addHandler(text_edit_handler)

        if not os.path.isdir(self.run_path):
            os.mkdir(self.run_path)
        log_file_path = os.path.join(self.run_path, "UI.log")
        file_handler = logging.FileHandler(log_file_path)
        self.LOGGER.addHandler(file_handler)

    def choose_image(self):
        self.input_image_path,_ = QFileDialog.getOpenFileName(self,"选择图片")
        self.imgPathText.setText(self.input_image_path)
        self.LOGGER.info(f"Select {self.input_image_path}")
        try:
            self.input_image = cv2.imread(self.input_image_path)
            self._show_image(self.input_image)
            self.current_image_path = self.input_image_path
            img_name = os.path.basename(self.current_image_path)
            self.current_image_name = ".".join(img_name.split(".")[:-1])

        except:
            self.LOGGER.info(f"Invalid,Please choose a Picture")

    def open_directory(self):
        self.selected_dir = QFileDialog.getExistingDirectory(self)
        try:
            self.imgPathText.setText(self.selected_dir)
            self.input_images_path = []

            for item in os.listdir(self.selected_dir):
                if os.path.basename(item).split('.')[-1].lower() in self.valid_images_format:
                    self.input_images_path.append(os.path.join(self.selected_dir, item))
            self.num_of_images = len(self.input_images_path)
            self.LOGGER.info(f"Detect there are {self.num_of_images} pictures at {self.selected_dir}")
        except:
            self.LOGGER.info(f"Invalid,Please choose a Directory")


    def detect(self):
        self.output_images_path = os.path.join(self.run_path, "images")
        if not os.path.isdir(self.output_images_path):
            os.mkdir(self.output_images_path)
        path = self.imgPathText.text()
        if os.path.isdir(path):
            index = 0
            for image_path in self.input_images_path:
                self.current_image_path = image_path
                img_name = os.path.basename(self.current_image_path)
                self.current_image_name = ".".join(img_name.split(".")[:-1])
                self.detect_dish(self.current_image_path)
                index+=1
                self._callback(int((index/self.num_of_images)*100))

        elif os.path.isfile(path):
            self.detect_dish(self.current_image_path)
        # self.detect_bacteria(self.dish_img_path)

    def detect_dish(self,img_path,yolo:bool=True):
        """
        detect dish from img
        :param img_path: image path
        :return:
        """
        img = cv2.imread(img_path)
        if yolo:
            # self.detect_circle_thread = DetectThread(yolo_dish(img_path,self.run_path))
            [flag,img] = yolo_dish(img_path,self.run_path)
            if not flag:
                self.LOGGER.info(f"Can't detect dish from {self.current_img_path}")
            dish_img_name = self.current_image_name + "_dish.png"
            self.dish_img_path = os.path.join(self.output_images_path, dish_img_name)
            cv2.imwrite(self.dish_img_path, img)
            self.LOGGER.debug(f"save preprocessed image at {self.dish_img_path}")
            self.detect_bacteria(self.dish_img_path)
        else:
            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            rows, cols = gray_img.shape
            min_r = int(min(rows,cols)/5)
            max_r = int(3*min(rows,cols)/5)
            self.detect_circle_thread = DetectThread(get_dish(img=img,min_r=min_r,max_r=max_r))
            self.detect_circle_thread.work_finished.connect(self.detect_dish_finished)
            self.detect_circle_thread.start()
            self.LOGGER.debug(f"Trying to get dish from img {img_path}")


    def detect_dish_finished(self,result_list):
        [flag,img] = result_list
        self._show_image(img)
        self.countLabel.setText("")
        self.detect_circle_thread.wait()
        self.detect_circle_thread.quit()
        self.detect_circle_thread.wait()
        self.detect_circle_thread.deleteLater()
        if not flag:
            self.LOGGER.info(f"Can't detect dish from {self.current_img_path}")
        dish_img_name = self.current_image_name + "_dish.png"
        self.dish_img_path = os.path.join(self.output_images_path,dish_img_name)
        cv2.imwrite(self.dish_img_path,img)
        self.LOGGER.debug(f"save preprocessed image at {self.dish_img_path}")

        self.detect_bacteria(self.dish_img_path)

    def detect_bacteria(self,dish_img_path):
        img = cv2.imread(dish_img_path)
        opt = detect.parse_opt()
        opt.imgsz = [int(img.shape[1]/32)*32,int(img.shape[0]/32)*32]
        opt.project = self.run_path
        opt.source = dish_img_path
        opt.weights = os.path.join(ROOT,"weights","23-3-7.pt")
        # opt.cfg = os.path.join(ROOT,"models","YoloBcc.yaml")
        detect.run(**vars(opt))

        self.result_csv = os.path.join(self.run_path, "result.csv")
        self.labels_pth = os.path.join(self.run_path, "exp", "labels", self.current_image_name + "_dish.txt")
        self.result_img = os.path.join(self.run_path, "exp", self.current_image_name + "_dish.png")
        self.result_path = os.path.join(self.run_path, "result")
        self.result_process()

    def result_process(self):
        if not os.path.isdir(self.result_path):
            os.mkdir(self.result_path)
        if os.path.isfile(self.labels_pth):
            with open(self.labels_pth, "r") as f:
                label_list = f.readlines()
                bacteria_counts = len(label_list)
                f.close()
            _force_move(self.labels_pth,self.result_path)
        else:
            bacteria_counts = 0
        self.csv_pairs.append([self.current_image_name + '.png', bacteria_counts])
        self.LOGGER.info(f"{self.current_image_name}.png 's bacteria num is {bacteria_counts}")

        with open(self.result_csv,'a') as f1:
            f1.write(f"{self.current_image_name}_dish.png,{bacteria_counts}\n")
            f1.close()
        result_img = cv2.imread(self.result_img)
        self.countLabel.setText(f"{bacteria_counts}")
        self._show_image(result_img)

        _force_move(self.dish_img_path, self.result_path)
        _force_move(self.result_img, self.output_images_path)
        shutil.rmtree(os.path.join(self.run_path,"exp"))

    def _show_image(self,input_image):
        """
        display image on GUI
        :param image: cv2 image
        :return:
        """
        display = cv2.resize(input_image, (self.display_size.width(), self.display_size.height()))
        img = cv2.cvtColor(display,cv2.COLOR_BGR2RGB)
        self.display_image = QtGui.QImage(img.data,img.shape[1],img.shape[0],QtGui.QImage.Format_RGB888)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.display_image))
        QApplication.processEvents()

    def _callback(self,proc:int=0):
        """

        :param proc:
        :return:
        """
        self.progressBar.setProperty("value",proc)
        QApplication.processEvents()

def _force_move(src_path:str,des_path:str):
    """
    force move file ,if des_path exists src file,it will replace it
    :param src_path:
    :param des_path:
    :return:
    """
    src_base_name = os.path.basename(src_path)
    if os.path.isfile(des_path):
        if os.path.basename(des_path) == src_base_name:
            os.remove(des_path)
        else:
            shutil.move(src_path,des_path)
    elif os.path.isdir(des_path):
        if os.path.isfile(os.path.join(des_path,src_base_name)):
            os.remove(os.path.join(des_path,src_base_name))
        else:
            shutil.move(src_path,des_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller_gui = myMainWindow()
    controller_gui.show()
    sys.exit(app.exec_())