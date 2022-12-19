import cv2
import glob
import os

IMG_SIZE = (200, 200)

#画像をくっつける
def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

#slide_filesに入っているパスの画像を全てくっつける
def createTile(slide_files):
    im_list = []
    for file in slide_files:
        img = cv2.imread(file)
        IMG_SIZE = (200, 200)
        img = cv2.resize(img, IMG_SIZE)
        im_list.append(img)
    im_tile = concat_tile([im_list])
    
    return im_tile


#pathと一致する画像があったらそれを返す
def findImg(path, slide_files):
    img_tile = createTile(slide_files)
    H, W, C = img_tile.shape
    
    img = cv2.imread(path)
    img = cv2.resize(img, (200,200))
    h, w, c = img.shape
    
    result = cv2.matchTemplate(img, img_tile, cv2.TM_CCOEFF_NORMED).tolist()
    result_index = result[0].index(max(result[0]))
    
    if result_index%200== 0 and max(result[0]) > 0.98:
        return_path = slide_files[result_index//200]
    else: return_path = None
    
    return return_path

    
def findSimilarFiles(folder_path):
    similar_files = []
    folder_files = sorted(glob.glob(f'{folder_path}/*.jpg'))
    for index, path in enumerate(folder_files):
        slide_files = [f for f in folder_files[index-2:index]+folder_files[index+1:index+3]]
        #print(folder_files)
        #slide_files.remove(path)
        sim_path = findImg(path, slide_files)
        if sim_path:
            #もう既にペアになっているかチェック
            isin = False
            for sim_i, sim in enumerate(similar_files):
                if (path in sim) or(sim_path in sim):
                    sim.add(path)
                    sim.add(sim_path)
                    isin = True
            if isin==False:similar_files.append({path, sim_path})
    return similar_files

def createCorrectSlides(folder_path):
    similar_files = findSimilarFiles(folder_path)
    
    files = set(glob.glob(f'{folder_path}/*'))
    for sim in similar_files:
        files = files-sim
        #ラストのものだけを追加する
        files.add(sorted(list(sim))[-1])
    
    save_path = '/'.join(folder_path.split('/')[:-1])+ '/correct_slides'
    os.system(f'mkdir -p {save_path}')
    #正しいファイルをコピーする
    for file in files:
        os.system(f'cp {file} {save_path}')
        
    return save_path
        

        
