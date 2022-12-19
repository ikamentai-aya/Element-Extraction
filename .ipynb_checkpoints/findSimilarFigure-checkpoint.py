import glob
from code_data.reomoveSimilarSlide import createTile
from code_data.deriveSlideFigure import createSubFigure
import cv2
import pickle

#pathと一致する画像があったらそれを返す
def findSimilarImg(path, img_tile):
    
    img = cv2.imread(path)
    # if img==None:
    #     print(path)
    #     return []
    img = cv2.resize(img, (200,200))
    part_img_list, bounding_img = createSubFigure(path)
    result_index_set = set(findSimilarSubImg(img, img_tile))
    for part_img in part_img_list:
        h, w, c = part_img.shape
        if h > 100 and w > 100:
            part_img = cv2.resize(part_img, (200,200))
            result_index = findSimilarSubImg(part_img, img_tile)
            result_index_set = set(result_index)|result_index_set
        
    return result_index

def findSimilarSubImg(img, img_tile):
    H, W, C = img_tile.shape
    
    h, w, c = img.shape
    
    result = cv2.matchTemplate(img, img_tile, cv2.TM_CCOEFF_NORMED).tolist()
    max_index = result[0].index(max(result[0]))
    max_similar = max(result[0])
    
    result_index = []
    #while result[0][max_index] > 0.7:
    while abs(max_index%200)<5:
        result_index.append(max_index//200)
        result[0][max_index]=0
        max_index = result[0].index(max(result[0]))
        max_similar = max(result[0])
    
    return result_index


def findSimilarFigures(file_name):
    report_figure_path = f'pvis_data/addtion_data/{file_name}/report_content/figure/*.jpg'
    report_figures = sorted(glob.glob(report_figure_path))
    slide_figure_path = f'pvis_data/addtion_data/{file_name}/video_content/correct_slides_figure/*.jpg'
    slide_figures = sorted(glob.glob(slide_figure_path))
    
    #スライドに出てきた画像を全てくっつける
    img_tile = createTile(slide_figures)
    print(len(slide_figures))
    
    similar_pair = []
    for r_figure in report_figures:
        sim_figure_index = findSimilarImg(r_figure, img_tile)
        print(sim_figure_index)
        for index in sim_figure_index:
            similar_pair.append([r_figure, slide_figures[index]])
            
    save_path = f'pvis_data/addtion_data/{file_name}/report_content/figure_taiou.pickle'
    #save_path = 'pvis_data/addtion_data/note-1020/video_content/slide_txt.pickle'
    with open(save_path, mode='wb') as f:
        pickle.dump([similar_pair], f)
    