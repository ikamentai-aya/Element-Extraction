from pathlib import Path
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import os
import pickle
import matplotlib as plt
import pyocr
from IPython.display import Markdown, display, clear_output
import re

#座標とページ番号を渡すと、色を塗って返してくれる
def highlight(space, page_number, save_path):
    
    original = cv2.imread(f'{save_path}/{page_number}.jpg')
    
    for coodinate in space:
        height = coodinate[1]-coodinate[0]
        width = coodinate[3]-coodinate[2]
        
        #ブランク画像
        blank = np.zeros((height, width, 3))
        blank += [255,236,0][::-1] #RGBで青指定
        
        y_offset = coodinate[0]
        x_offset = coodinate[2]
        original[y_offset:y_offset+height, x_offset:x_offset+width] = original[y_offset:y_offset+height, x_offset:x_offset+width]*0.8+blank*0.2
        
    image = Image.fromarray(original)
    return image
    

# def findSpace(input_text, path_coordinate_dict, path_text_dict):
#     word_list = input_text.split()
#     word_num = len(word_list)
#     coodinate = []
#     page = 0
#     for i in path_coordinate_dict:
#         txt_words = path_text_dict[i].split()
        
#         if txt_words[:word_num]==word_list or input_text in path_text_dict[i]:
#             coodinate = path_coordinate_dict[i]
#             page=i.split('/')[-1].split('-')[0]
            
#     return coodinate, page
            
# #ハイライトしたい部分の先頭を与えると、ハイライトした画像で返してくれる
# def highlightTextList(index_list, text_list, path_coordinate_dict, path_text_dict, save_path):
#     c_p_list = []
#     for text in text_list:
#         coodinate, page = findSpace(text, path_coordinate_dict, path_text_dict)
#         if [coodinate, page] in c_p_list:continue
#         if len(coodinate) == 0:
#             continue
#         c_p_list.append([coodinate, page])
        
#     p_c_dict = dict()
#     for c, p in c_p_list:
#         if p in p_c_dict:p_c_dict[p].append(c)
#         else: p_c_dict[p] = [c]
        
#     image_list = []
#     for p in p_c_dict: 
#         image = highlight(p_c_dict[p], p, save_path)
#         image_list.append(image)
        
#     page_list = [p for p in p_c_dict]
    
#     return image_list, page_list, p_c_dict

def findSpace(index, paragraph_coordinate_dict, new_area_section_index):
    for i, path in enumerate(new_area_section_index):
        if index in new_area_section_index[path]:
            page = path.split('/')[-1].split('-')[0]
            print(path, page, index)
            coodinate = paragraph_coordinate_dict[path]
            return page, coodinate
    

def highlightCluster(file_name):
    
    wordcloud_path = f'pvis_data/addtion_data/{file_name}/wordcloud'

    ##クラスターの情報を取得する
    with open(f'{wordcloud_path}/cluster.pickle', mode='rb') as f:
        [group] = pickle.load(f)
        
    ## 文章のインポート
    report_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    with open(report_path, mode='rb') as f:
        [content, section_title, addtion]=pickle.load(f)
        
    ##レイアウト情報のインポート
    save_path = f'pvis_data/addtion_data/{file_name}/report_content/content'
    with open(save_path+'/path_coordinate.pickle', mode='rb') as f:
        [path_coordinate_dict, path_text_dict] = pickle.load(f)
        
    ##小領域に変更したもののimport##
    with open(f'pvis_data/addtion_data/{file_name}/report_content/coordinate.pickle', mode='rb') as f:
        [paragraph_coordinate_dict, non_paragraph_coordinate_dict, new_area_section_index] = pickle.load(f)
    print(new_area_section_index)
    
    page_coordinate_list = dict()
    for cluster_num in group:
        text_list = []
        p_c_dict = dict()
        page_list = set()
        for i in group[cluster_num]:
            if i < len(content):
                s = ' '.join(content[i].split()[0:3])
                if re.match(r'[0-9a-zA-Z]', s[0])==None:s = ' '.join(content[i].split()[1:4])
                text_list.append(s)
                # どこに属するのかを探す
                res = findSpace(i, paragraph_coordinate_dict, new_area_section_index)
                if res:
                    page, coodinate = res
                    page_list.add(page)
                    if page in p_c_dict: p_c_dict[page].append(coodinate)
                    else: p_c_dict[page]= [coodinate]
        
        image_list = []
        for p in p_c_dict: 
            image = highlight(p_c_dict[p], p, save_path)
            image_list.append(image)
        page_list = sorted(list(page_list))
        
    
#         image_list, page_list, p_c_list = highlightTextList(group[cluster_num],text_list, path_coordinate_dict, path_text_dict, save_path)
        page_coordinate_list[cluster_num]=[]
        cluster_folder = f'pvis_data/addtion_data/{file_name}/wordcloud/{cluster_num}'
        os.makedirs(cluster_folder, exist_ok=True)
        for image, page in zip(image_list, list(page_list)):
            image.save(f'{cluster_folder}/{page}.jpg')
            
    ## ページ数とそれに含まれる段落に関する情報を保存する
    with open(f'pvis_data/addtion_data/{file_name}/wordcloud/page_cluster.pickle', mode='wb') as f:
        pickle.dump([page_coordinate_list],f)
    
    
