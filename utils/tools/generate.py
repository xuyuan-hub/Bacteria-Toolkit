import os
import glob
import shutil

def generate_dataset(src_path:str,des_path:str,train_weight:float=0.7,test_weight:float=0.2,valid_weight:float=0.1):
    """
    generate dataset
    :param src_path:
    :param des_path:
    :param train_weight:
    :param test_weight:
    :param valid_weight:
    :return:
    """
    valid_img_suf = ["png","Tif","jpg","tif"]
    if os.path.isdir(src_path):
        if not os.path.isdir(des_path):
            os.mkdir(des_path)
        datasets = ["train","test","val"]
        dataset_w = [train_weight,test_weight,valid_weight]
        dataset_path = []
        samples = []
        for d in datasets:
            d_path = os.path.join(des_path,d)
            if not os.path.isdir(d_path):
                os.mkdir(d_path)
            dataset_path.append(d_path)

        for file in glob.glob(src_path+"\\*.txt"):
            basename = os.path.basename(file)
            samples.append(".".join(basename.split('.')[:-1]))
        samples_count = len(samples)
        index=0
        set_id = 0
        for sample in samples:
            if index/samples_count > dataset_w[set_id]:
                set_id += 1
                dataset_w[set_id] += dataset_w[set_id - 1]
            images_path = os.path.join(dataset_path[set_id],"images")
            labels_path = os.path.join(dataset_path[set_id],"labels")
            if not os.path.isdir(images_path):
                os.mkdir(images_path)
            if not os.path.isdir(labels_path):
                os.mkdir(labels_path)
            shutil.copy(os.path.join(src_path,sample+'.txt'),
                        os.path.join(labels_path,sample+'.txt'))
            for valid_img in valid_img_suf:
                img_name = sample+"."+valid_img
                if os.path.isfile(os.path.join(src_path,img_name)):
                    shutil.copy(os.path.join(src_path,img_name),os.path.join(images_path,img_name))
                    break
            index += 1


if __name__ == '__main__':
    src_path = r"C:\Users\huihongyuan\PycharmProjects\BacteriaToolkit\ColonyCounter\data\images\dish\dish0818"
    des_path = r"C:\Users\huihongyuan\PycharmProjects\BacteriaToolkit\ColonyCounter\data\images\dish\dishset"
    generate_dataset(src_path=src_path,des_path=des_path)
