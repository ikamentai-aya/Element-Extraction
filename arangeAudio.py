####AWS transcribeで得たものを形成する関数####
import json
import pickle
import glob
import re

#スライドと文字起こしの紐付け
def stickSlide(sentense_list, file_num_index):
    index = 0
    slide_sentense_index = [[] for i in file_num_index]
    for s_i, i in enumerate(sentense_list):
        if i['end']<file_num_index[index]:slide_sentense_index[index].append(s_i)
        else:
            if index == len(file_num_index)-1:slide_sentense_index[index].append(s_i)
            elif i['start'] > file_num_index[index]:slide_sentense_index[index+1].append(s_i)
            elif file_num_index[index]-i['start'] > i['end']- file_num_index[index]:
                slide_sentense_index[index].append(s_i)
            else: slide_sentense_index[index+1].append(s_i)
            index = min(len(file_num_index)-1, index+1)
            print(i['content'], f'{i["start"]}~{i["end"]}', file_num_index[index-1])
            
    print(slide_sentense_index)
    return slide_sentense_index
    

##jsonのpathを渡す
def arangeAudio(audio_path, slide_path):
    #音声の文字起こし結果の読み込み
    with open(audio_path) as f:
        transcript = json.load(f)
    transcript_result = transcript['results']
    t = transcript_result['transcripts'][0]['transcript']
    items = transcript_result['items'][:-1]
    
    item_list = transcript_result['items']
    start_time_list = [item['start_time'] if 'start_time' in item else None for item in item_list ]
    end_time_list = [item['end_time'] if 'end_time' in item else None for item in item_list ]
    
    ##文に分割する
    sentense_list = []
    now_senetense = []
    start_time = 0.0
    for index, item in enumerate(items):
        isEnd = False #文の最後か
        now_senetense.append(item['alternatives'][0]['content'])
        
        next_item = transcript_result['items'][index+1]
        if not 'end_time' in item.keys(): isEnd = True
        else: end_time=float(item['end_time'])
        
        ##次がカンマだった場合
        if not 'start_time' in next_item.keys():continue
        ##次までに時間が空いていた場合
        elif float(next_item['start_time'])-end_time>0.01:isEnd = True
        
        if isEnd:
            sentense_list.append(dict(content=' '.join(now_senetense), start=start_time, end = float(end_time)))
            start_time = float(next_item['start_time'])
            now_senetense = []
            
    ##最後の文の処理
    last_item = items[-1]
    now_senetense.append(last_item['alternatives'][0]['content'])
    sentense_list.append(dict(content=' '.join(now_senetense), start=start_time, end = float(last_item['end_time'])))
            
    ##スライドとの対応を考える
    slide_files = sorted(glob.glob(f'{slide_path}/*.jpg'))
    #正規表現で秒数を取得
    file_num_pt = re.compile('image_([0-9]+).jpg')

    file_num_index = []
    for file in slide_files:
        last = file.split('/')[-1]
        m = file_num_pt.match(last)
        file_num_index.append(10*int(m.group(1))+5)
            
    slide_sentense_index = stickSlide(sentense_list, file_num_index)
    new_sentense_list = [s['content'] for s in sentense_list]
    s_start_time_list = [s['start'] for s in sentense_list]
    s_end_time_list = [s['end'] for s in sentense_list]
    
    save_path = '/'.join(audio_path.split('/')[:-1])+'/slide_audio.pickle'

    with open(save_path, mode="wb") as f:
        pickle.dump([new_sentense_list, s_start_time_list, s_end_time_list, slide_sentense_index], f)
    