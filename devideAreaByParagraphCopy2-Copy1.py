import pickle
import cv2
import numpy as np
import os
from PIL import Image
import shutil
import re
import statistics
import glob


# 各領域に所属する段落を発見し、発見したらそのインデックスを返す
def findAreaIndex(path_coordinate_dict, path_text_dict, content, section_title):
  area_index = dict()
  area_section_index = dict()
  path_text_words = dict()
  for path in path_coordinate_dict:
      area_index[path] =[]
      area_section_index[path] = []
      path_text_words[path] = set(path_text_dict[path].split())
      
  #一番一致する単語数の多い領域に包含されていると考える
  for i, c in enumerate(content):
      isIn = False
      if len(c) < 30: continue
      sub_string = round(len(c)*0.8)
      for path in path_coordinate_dict:
          if not '.' in path_text_dict[path]:continue
          if c[:40] in path_text_dict[path][:50]:
              if '3-0' in path: print(path_text_dict[path])
              area_index[path].append(i)
              isIn = True
              break
      if not isIn:
          for path in path_coordinate_dict:
              if not '.' in path_text_dict[path]:continue
              if c[10:50] in path_text_dict[path]:
                  if '3-0' in path: 
                    print('------\n'+path_text_dict[path]+'------\n')
                  if i== 12:
                      print(c)
                  area_index[path].append(i)
                  isIn = True
                  break
      if not isIn: 
          for path in path_coordinate_dict:
              if not '.' in path_text_dict[path]:continue
              if c[10:50] in path_text_dict[path].replace('\n', ' '):
                  if '3-0' in path: 
                    print('------\n'+path_text_dict[path]+'------\n')
                  if i== 12:
                      print(c)
                  area_index[path].append(i)
                  isIn = True
                  break
      if not isIn: print(c)

  #section_titleが入っている可能性も鑑みる
  for s in section_title: 
    for path in path_coordinate_dict:
      if s[0] in path_text_dict[path]:
          area_section_index[path].append(s[0])
          break

  return area_index, area_section_index

# 各領域を段落の行数から分割する
def splitArea(path_coordinate_dict, path_text_dict, content, path, index_list, save_path, section_index):
  img = cv2.imread(path)
  height, width, channels = img.shape[:3]
  file_name = path.split('/')[-1].split('.')[0]
  
  #領域内の文章を取得
  area_txt = path_text_dict[path]
  area_txt = area_txt.replace('\n\n', '\n')

  #セクションタイトルは三行分のスペースを取るので調整
  for s in section_index:
    area_txt = area_txt.replace(s, f'-\n{s}\n-')
  
  #index_listをもとに分割位置を記載する
  line_list = area_txt.split('\n')
  for line in line_list:
    for index in index_list:
      c = content[index]
      if c[:20] in line or c[10:30] in line: 
        area_txt = area_txt.replace(line, f'\n{line}')

  #if len(section_index) > 0:print(area_txt)
  #空行が入ったら分割
  area_txt_paragraphs = area_txt.split('\n\n')
  area_txt_paragraphs = [t for t in area_txt_paragraphs if t != '']
  
  kireme = [] #段落がどこで切れているのか
  now = 0
  
  for t in area_txt_paragraphs:
    t_list = t.split('\n')
    t_list = [t_i for t_i in t_list if t_i != '']
    p_num = len(t_list) #段落tの行数
    kireme.append(now+p_num)
    now += p_num
  total_line_num = kireme[-1] #見ている領域の段落数

  height_list = [round(i*height/total_line_num) for i in kireme]
  print(sum(height_list), height_list)

  new_path_coordinate_dict = dict()
  #print(height_list, height, width)
  height_list = sorted(list(set(height_list)))
  
  [c_t, c_b, c_l, c_r] = path_coordinate_dict[path]
  top = 0
  print(path)
  for i, h in enumerate(height_list):
    print(top, min(h,height), 0, width)
    image = Image.fromarray(img[top:min(h,height), 0:width])
    
    image.save(f'{save_path}/{file_name}-{i}.jpg')
    new_path_coordinate_dict[f'{save_path}{file_name}-{i}.jpg'] = [c_t+top, c_t+h, c_l, c_r]
    top = h
    
  return new_path_coordinate_dict
  

##このモジュールのメイン関数
def deriveArea(coodinate_path, content_path):
  with open(coodinate_path, mode='rb') as f:
    [path_coordinate_dict, path_text_dict] = pickle.load(f)
  
  with open(content_path, mode='rb') as f:
    [content, section_title, addition] = pickle.load(f)

  area_index, area_section_index = findAreaIndex(path_coordinate_dict, path_text_dict, content, section_title)
  
  #段落を表す領域の保存場所
  save_path = '/'.join(coodinate_path.split('/')[:-2])
  os.makedirs(f'{save_path}/paragraph', exist_ok=True)
  os.makedirs(f'{save_path}/not_paragraph', exist_ok=True)

  paragraph_coordinate_dict = dict()
  non_paragraph_coordinate_dict = dict()
  non_paragraph_text_dict = dict()
  for path in area_index:
    if area_index[path] != []:
      new_path_coordinate_dict = splitArea(path_coordinate_dict, path_text_dict, content, path, area_index[path], f'{save_path}/paragraph/', area_section_index[path])
      paragraph_coordinate_dict |= new_path_coordinate_dict
      #if len(area_index[path])>2:print(path_text_dict[path])
    elif area_section_index[path] == []:
      file_name = path.split('/')[-1]
      shutil.copyfile(path, f'{save_path}/not_paragraph/{file_name}')
      non_paragraph_coordinate_dict[f'{save_path}/not_paragraph/{file_name}'] = path_coordinate_dict[path]
      non_paragraph_text_dict[f'{save_path}/not_paragraph/{file_name}'] = path_text_dict[path]

  before_files = sorted(glob.glob(f'{save_path}/content/*.jpg'))
  for file in before_files:
    file_name = file.split('/')[-1]
    if not '-' in file_name:shutil.copyfile(file, f'{save_path}/not_paragraph/{file_name}')

  with open(f'{save_path}/coordinate.pickle', mode='wb') as f:
    pickle.dump([paragraph_coordinate_dict, non_paragraph_coordinate_dict, area_section_index],f)
  with open(f'{save_path}/not_paragraph/coordinate.pickle', mode='wb') as f:
    pickle.dump([non_paragraph_coordinate_dict, non_paragraph_text_dict],f)

coodinate_path = input()
content_path = input()
deriveArea(coodinate_path, content_path)

