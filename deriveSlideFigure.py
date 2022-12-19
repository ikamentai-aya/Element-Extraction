from PIL import Image
import os
import cv2
import glob
import numpy as np

##画像のパスを受け取り領域分割する
def createSubFigure(jpeg_path):
    #画像の読み込み
    img = cv2.imread(jpeg_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #ガウシアンでぼかす
    img_blur = cv2.GaussianBlur(gray_img, (41,41), 0)

    #画像を２値化する
    _, threshold_img = cv2.threshold(img_blur, 248, 255, cv2.THRESH_BINARY)
    
    
    #白黒反転する
    reversal_img = cv2.bitwise_not(threshold_img)
    
    #大体の輪郭を取り出す
    contours, _ = cv2.findContours(reversal_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #部分の切り出し
    part_img_list = []
    bounding_img = np.copy(img)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_img = cv2.rectangle(bounding_img, (x, y), (x + w , y + h), (0,255, 0), 3)
        part_img = img[y:y+h, x:x+w]
        part_img_list.append(part_img)
        
    return part_img_list, bounding_img

#folder_pathにあるスライドの画像から自動で全ての画像を取ってくる
def deriveSlideFigure(folder_path):
    path_list = sorted(glob.glob(f'{folder_path}/*.jpg'))
    save_folder = folder_path+'_figure'
    os.system(f'mkdir -p {save_folder}')
    
    #全ての画像で分割を行う
    for path in path_list:
        path_split = path.split('/')
        save_path = save_folder +'/'+ path.split('/')[-1].split('.')[0]
        
        new_parts, bounding_img = createSubFigure(path)

        for i, img in enumerate(new_parts):
            #image = Image.fromarray(img)
            #image.save(f'{save_path}-{i}.jpg')
            cv2.imwrite(f'{save_path}-{i}.jpg',img)

    figure_files = sorted(glob.glob(f"{save_folder}/*.jpg"))
    for file in figure_files:
        size = os.path.getsize(file)
        if size < 25000: os.remove(file)
        
        
#folder_path = input()
#deriveSlideFigure(folder_path)