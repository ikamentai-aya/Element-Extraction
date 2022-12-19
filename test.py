from PIL import Image
import os
import cv2
import glob
import numpy as np

##画像のパスを受け取り領域分割する
def createSubFigure(jpeg_path, back_ground_color):
    img = cv2.imread(jpeg_path)
    #img = cv2.resize(img, (200,200))
    int_img = img.astype(np.int64)
    c_img = img-back_ground_color
    c_img = np.abs(c_img).astype(np.uint8)

    gray_img = cv2.cvtColor(c_img.astype(np.uint8), cv2.COLOR_BGR2GRAY)

    #ガウシアンでぼかす
    img_blur = cv2.GaussianBlur(gray_img, (31,31), 0)

    #画像を２値化する
    _, threshold_img = cv2.threshold(img_blur, 8, 255, cv2.THRESH_BINARY)

    #大体の輪郭を取り出す
    contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
def deriveSlideFigure(file_name):
    slide_path = f'pvis_data/addtion_data/{file_name}/video_content/correct_slides/*.jpg'
    slide_files = sorted(glob.glob(slide_path))
    
    save_folder = f'pvis_data/addtion_data/{file_name}/video_content/figure'
    os.system(f'mkdir {save_folder}')
    
    ##背景色を探す##
    ##各頂点のグリッド上点の色を持ってくる
    for slide in slide_files:
        img = cv2.imread(slide)
        img = cv2.resize(img, (200,200))
        h, w, c = img.shape
        fourpoint = [0, 49,99,149,199]
        point_color = []
        for x in fourpoint:
            for y in fourpoint:
                color = img[x,y]
                color = [str(i) for i in color]
                point_color.append('-'.join(color))
    point_color = np.array(point_color)
    unique, freq = np.unique(point_color, return_counts=True)
    freq = freq.tolist()
    max_index = freq.index(max(freq))
    back_ground_color = unique[max_index].split('-')
    back_ground_color = np.array([int(c) for c in back_ground_color])
    
    ##全ての画像で分割を行う##
    for slide in slide_files:
        save_path = save_folder +'/'+ slide.split('/')[-1].split('.')[0]
        new_parts, bounding_img = createSubFigure(slide, back_ground_color)

        for i, img in enumerate(new_parts):
            cv2.imwrite(f'{save_path}-{i}.jpg',img)

    figure_files = sorted(glob.glob(f"{save_folder}/*.jpg"))
    for file in figure_files:
        size = os.path.getsize(file)
        if size < 25000: os.remove(file)
        
        
#folder_path = input()
#deriveSlideFigure(folder_path)


file_name = input()

deriveSlideFigure(file_name)




