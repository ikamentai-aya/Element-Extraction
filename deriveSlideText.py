from PIL import Image
import pyocr
import glob
import pickle
import os

# OCRエンジンを取得
engines = pyocr.get_available_tools()
engine = engines[0]

#folder_pathのフォルダに入った
def deriveSentense(folder_path):
    path_list = sorted(glob.glob(f'{folder_path}/*.jpg'))
    txt_list = []
    
    for path in path_list:
        # 画像の文字を読み込む
        txt = engine.image_to_string(Image.open(path), lang="eng")
        txt_list.append(txt)
        
    save_path = '/'.join(folder_path.split('/')[:-1])+'/slide_txt.pickle'
    if os.path.exists(save_path): os.remove(save_path)
    print(os.path.exists(save_path))
    with open(save_path, mode='wb') as f:
        pickle.dump([txt_list], f)
    