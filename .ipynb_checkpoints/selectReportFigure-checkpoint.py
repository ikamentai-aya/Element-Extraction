import pickle
from PIL import Image
import cv2
import glob
import os
import shutil
import re
import pyocr
import time

engines = pyocr.get_available_tools()
engine = engines[0]

def 分類(path, coodinate_dict, path_text_dict):
    name_pt = re.compile('table [0-9]+|figure [0-9]+|fig [0-9]+')
    fig_table_words=['fig', 'table', 'figure']
    #txt = engine.image_to_string(Image.open(path), lang="eng")
    txt = path_text_dict[path]
    txt_line = txt.split('\n\n')
    
    s_line = txt_line[0].replace('\n', ' ').lower()
    l_line = txt_line[-1].replace('\n', ' ').lower()
    isFig = False
    for word in fig_table_words:
        if s_line.startswith(word):isFig = True
        if l_line.startswith(word):isFig = True
    txt_number = len(txt.split('\n')) #何段落あるのか
    height = coodinate_dict[path][1]-coodinate_dict[path][0]
    width = coodinate_dict[path][3]-coodinate_dict[path][2]
    
    return isFig, len(txt_line), txt, height*width, height

#path2の画像がpath1の画像の上にある画像か判定
def isAboveFigure(path1, path2, coodinate_dict):
    
    [y1_1, y2_1, x1_1,x2_1] = coodinate_dict[path1]
    [y1_2, y2_2, x1_2,x2_2] = coodinate_dict[path2]
    
    #縦並びか
    sort_x, sort_index = zip(*sorted(zip([x1_1,x2_1,x1_2,x2_2], [1,1,2,2])))
    if not(sort_index==(1,1,2,2) or sort_index==(2,2,1,1)):
        if y1_2 < y2_1:
            return True, y2_1-y1_2
        else: return False, -1
    else:return False, -1

#二つの四角形が横並びか判定
def isHorizontal(area1, area2):
    [y1_1, y2_1, x1_1,x2_1] = area1
    [y1_2, y2_2, x1_2,x2_2] = area2
    bound = [min(y1_1,y1_2),max(y2_1,y2_2), min(x1_1,x1_2),max(x2_1,x2_2)]
    
    #横並びか
    sort_y, sort_index = zip(*sorted(zip([y1_1,y2_1,y1_2,y2_2], [1,1,2,2])))
    if not(sort_index==(1,1,2,2) or sort_index==(2,2,1,1)):
        return bound
    else: return None
    
#横並びの画像をまとめる
def summarizeFigure(path_list,dis_list, coodinate_dict):
    
    horizontal_group = []
    group_area = []
    new_dis_list = []
    for p_index, path in enumerate(path_list):
        area1 = coodinate_dict[path]
        isGroup = False
        for group_index, area2 in enumerate(group_area):
            result = isHorizontal(area1, area2)
            if result!=None:
                horizontal_group[group_index].append(path)
                group_area[group_index] = result
                isGroup = True
                new_dis_list[group_index] = min(new_dis_list[group_index], dis_list[p_index])
                continue
        if not isGroup:
            horizontal_group.append([path])
            group_area.append(area1)
            new_dis_list.append(dis_list[p_index])
            
    sorted_dis_list, sorted_area = zip(*sorted(zip(new_dis_list, group_area)))
    return sorted_area[0]
            
    

#pathの直上の画像を探す
def findAbove(path, coodinate_dict):
    files = sorted(glob.glob('-'.join(path.split('-')[:2])+'-*.jpg'))
    files.remove(path)
    
    above_path = []
    above_dis = []
    for path2 in files:
        isAbove, dis = isAboveFigure(path, path2,coodinate_dict)
        if isAbove: 
            above_path.append(path2)
            above_dis.append(dis)
            
    if len(above_path) > 0:
        area = summarizeFigure(above_path,above_dis, coodinate_dict)
    else: area = None
    return area


def makeCorrectFigure(folder_path, coodinate_path):
    
    path = folder_path+'/*-*.jpg'
    #以前に保存した画像のpathとその座標を紐づける辞書を読み込む
    with open(coodinate_path, mode='rb') as f:
        [coodinate_dict,path_text_dict] = pickle.load(f)
        
    files = sorted(glob.glob(path))
    
    #画像を保存するフォルダを作成する
    save_path = '/'.join(path.split('/')[:-2])+'/figure'
    os.makedirs(save_path, exist_ok=True)
    
    name_pt = re.compile('table [0-9]+|figure [0-9]+|fig [0-9]+')
    
    figure_area_dict = {}
    for index, file in enumerate(files):
        page_num = file.split('/')[-1].split('-')[0]
        isFig,line_number,txt, area, height = 分類(file, coodinate_dict, path_text_dict)
        #最初の段落または最後の段落がfigure、tableのどちらかから始まっている時    
        if isFig:
            txt = txt.lower()
            names = name_pt.findall(txt)
            caption = names[0]
            
            #キャプションだった時
            #if line_number==1 or area/len(txt)<900:
            if line_number==1 or height < 300:
                #画像の座標を取り出し、その部分を保存する
                fig_area = findAbove(file, coodinate_dict)
                if fig_area == None: continue
                im = cv2.imread('-'.join(file.split('-')[:-1])+'.jpg')
                new_im = im[fig_area[0]:fig_area[1],fig_area[2]:fig_area[3]]
                image = Image.fromarray(new_im)
                cv2.imwrite(f'{save_path}/{caption}.jpg', new_im)
                figure_area_dict[caption] = [page_num,[fig_area[0],fig_area[1],fig_area[2],fig_area[3]]]
            #キャプションじゃないとき
            else:
                shutil.copyfile(file, f'{save_path}/{caption}.jpg')
                figure_area_dict[caption] = [page_num, coodinate_dict[file]]
    with open(f'{save_path}/coodinate.pickle', mode='wb') as f:
        pickle.dump([figure_area_dict], f)
        
def main():
    print('画像のフォルダを教えてください')
    folder_path = input()
    print('座標の保存したdictのフォルダを教えてください')
    coodinate_path = input()
    makeCorrectFigure(folder_path, coodinate_path)
