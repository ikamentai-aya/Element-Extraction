from pathlib import Path
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import os
import pickle
import pyocr

tools = pyocr.get_available_tools()

### PIL型 => OpenCV型　の変換関数
def pil2opencv(in_image):
    out_image = np.array(in_image, dtype=np.uint8)
    print(out_image.shape[2])
    if out_image.shape[2] == 3:
        out_image = cv2.cvtColor(out_image, cv2.COLOR_RGB2BGR)
    
    return out_image

### PDF => OpenCV型　の変換関数
def pdf2opencv(input_pdf_path, out_format = "png"):
    opencv_images = []
    
    ### PDF => PIL
    images = convert_from_path(pdf_path = input_pdf_path, dpi = 300, fmt = out_format)
    
    for image in images:
        ### PIL型 => OpenCV型
        opencv_images.append(pil2opencv(image))
        
    return opencv_images

## openCV型から、subFigureを作る
def createSubFigure(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    

    #ガウシアンでぼかす
    img_blur = cv2.GaussianBlur(gray_img, (51,51), 0)

    #画像を２値化する
    _, threshold_img = cv2.threshold(img_blur, 248, 255, cv2.THRESH_BINARY)
    
    
    #白黒反転する
    reversal_img = cv2.bitwise_not(threshold_img)
    
    #大体の輪郭を取り出す
    contours, _ = cv2.findContours(reversal_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #部分の切り出し
    part_img_list = []
    bounding_img = np.copy(img)
    
    new_square = abbreviateImage(contours)
    coordinate_list = []
    for s in new_square:
        x1,y1,x2,y2 = s
        bounding_img = cv2.rectangle(bounding_img, (x1, y1), (x2 , y2), (0,255, 0), 3)
        part_img = img[y1:y2, x1:x2]
        coordinate_list.append([y1,y2,x1,x2])
        part_img_list.append(part_img)
        
    return part_img_list, bounding_img, coordinate_list

#二つの四角が重なっているかの判定
def isOverlap(s1, s2):
    #二つの四角形のx座標y座標を
    x1_1, y1_1,x2_1,y2_1 = s1
    x1_2, y1_2,x2_2,y2_2 = s2
    
    #x座標が重なっているか
    x = [x1_1,x2_1,x1_2,x2_2]
    index = [1,1,2,2]
    x_sort,index_sort = zip(*sorted(zip(x,index)))
    if index_sort==(1,1,2,2) or index_sort==(2,2,1,1):
        return False
    
    #x座標が重なっているか
    y = [y1_1,y2_1,y1_2,y2_2]
    index = [1,1,2,2]
    y_sort,index_sort = zip(*sorted(zip(y,index)))
    if index_sort==(1,1,2,2) or index_sort==(2,2,1,1):
        return False
    
    return True

#画像候補から、小さい画像を消去、被っている画像に処理を施す
def abbreviateImage(contours):
    new_contour = []
    size = []
    #極端に小さい画像は消去,サイズの大きい順に変える
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w >= 20 and h >= 20:
            new_contour.append([x,y,x+w,y+h])
            size.append(w*h)
            
    size, new_contour = zip(*sorted(zip(size, new_contour),reverse=True))        
        
    #重なっている画像はないかな
    new_square=[new_contour[0]]
        
    for s1 in new_contour[1:]:
        [x1_1,y1_1,x2_1,y2_1]=s1
        isdouble=False
        for s2 in new_square:
            [x1_2,y1_2,x2_2,y2_2] = s2
            if isOverlap(s1, s2):
                new_square.remove(s2)
                new_square.append([min(x1_1,x1_2),min(y1_1,y1_2),max(x2_1,x2_2),max(y2_1,y2_2)])
                isdouble=True
        if not isdouble:new_square.append(s1)
        
    return new_square

#PDFのパスを与えてそこから画像を切り出す
def deriveFigure(path):
    fname = path.split('/')[-1].split('.')[0]
    save_path = f'pvis_data/addtion_data/{fname}/report_content/content'
    os.makedirs(save_path, exist_ok=True)
    path_coordinate_dict = dict()
    path_text_dict = dict()
    
    opencv_images = pdf2opencv(path)
    for i1, img in enumerate(opencv_images):
        part_img_list, bounding_img, coordinate_list = createSubFigure(img)
        #image = Image.fromarray(img)
        #image = Image.fromarray(bounding_img)
        #image.save(f'{save_path}/{i1}.jpg')
        cv2.imwrite(f'{save_path}/{i1}.jpg', img)
        
        for i2, parts_img in enumerate(part_img_list):
            #image = Image.fromarray(parts_img)
            #image.save(f'{save_path}/{i1}-{i2}.jpg')
            parts_img = cv2.cvtColor(parts_img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'{save_path}/{i1}-{i2}.jpg', parts_img) 
            #サイズが極端に小さい場合は論外
            size = os.path.getsize(f'{save_path}/{i1}-{i2}.jpg')
            if size < 10000: os.remove(f'{save_path}/{i1}-{i2}.jpg')
            else:
                tool = tools[0]
                res = tool.image_to_string(
                    Image.open(f'{save_path}/{i1}-{i2}.jpg')
                    ,lang="eng")
                path_coordinate_dict[f'{save_path}/{i1}-{i2}.jpg']=coordinate_list[i2] 
                path_text_dict[f'{save_path}/{i1}-{i2}.jpg']=res                
                   
    with open(save_path+'/path_coordinate.pickle', mode='wb') as f:
        pickle.dump([path_coordinate_dict, path_text_dict],f)
        
    return save_path, save_path+'/path_coordinate.pickle'
    
