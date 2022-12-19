from code_data.createFolder import createFolder
from code_data.deriveReportContent import deriveReport
from code_data.deriveReportFigure import deriveFigure
from code_data.selectReportFigure import makeCorrectFigure
from code_data.splitVideo import splitVideo
from code_data.reomoveSimilarSlide import createCorrectSlides
from code_data.deriveSlideFigure import deriveSlideFigure
from code_data.deriveSlideText import deriveSentense
import time
import shutil

def preprocessing(paper_path, video_path, file_name):
    
    time_list = []
    flow_list = ['論文の内容を抽出','論文を画像として領域分解','分割した領域から図表を判定','動画を10秒ごとに分割','被ったスライドを省略', 'スライドから画像を抽出','スライドから文を抽出']
    createFolder(file_name)
    time_list.append(time.time())
    deriveReport(paper_path)
    time_list.append(time.time())
    
    #論文を領域分割
    folder_path,coodinate_path = deriveFigure(paper_path)
    time_list.append(time.time())
    makeCorrectFigure(folder_path, coodinate_path)
    time_list.append(time.time())
    #論文のpdfを新しいフォルダに移動
    fname = paper_path.split('/')[-1].split('.')[0]
    save_path = f'pvis_data/addtion_data/{fname}/{fname}.txt'
    shutil.copyfile(paper_path, save_path)
    
    #動画を処理する
    slide_folder_path = splitVideo(video_path, 10)
    time_list.append(time.time())
    correct_slide_path = createCorrectSlides(slide_folder_path)
    print('--------------------')
    print(correct_slide_path)
    print('--------------------')
    time_list.append(time.time())
    deriveSlideFigure(correct_slide_path) #画像を取得
    time_list.append(time.time())
    deriveSentense(correct_slide_path)
    time_list.append(time.time())
    
    for index in range(len(time_list)-1):
        print(f'{flow_list[index]}:{time_list[index+1]-time_list[index]}')
    print('-----')
    print(time_list)

"""
file_name = input()
paper_path = f'session8/pdf/{file_name}.pdf'
video_path = f'session8/presentations/{file_name}.mp4'

main(paper_path, video_path, file_name)
"""