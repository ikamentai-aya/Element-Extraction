from sklearn import cluster
import numpy as np
import pickle
import os
from wordcloud import WordCloud

def findBestEps(vector):
    min_samples = 3
    max_eps = 0
    max_cluster = 0 
    
    for eps in np.arange(0.01, 1.0, 0.01):
        dbscan = cluster.DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        dbscan_dataset = dbscan.fit_predict(vector)
        cluster_num = max(list(dbscan_dataset))
        if cluster_num > max_cluster: 
            max_eps = eps
            max_cluster = cluster_num
    
    dbscan_dataset = cluster.DBSCAN(eps=max_eps, min_samples=min_samples, metric='cosine').fit_predict(vector)
    group = {}
    group_index = {}
    dbscan_dataset = dbscan_dataset.tolist()
    for i,g in enumerate(dbscan_dataset):
        if g == -1: continue
        
        if not g in group:group[g] = [i]
        else:group[g].append(i)
    
    return max_eps, group

def clustering(file_name):
    #文書ベクトルの取り出し
    save_path = f'pvis_data/addtion_data/{file_name}/vector.pickle'
    report_pickle_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    audio_pickle_path = f'pvis_data/addtion_data/{file_name}/video_content/slide_audio.pickle'
    
    with open(save_path, mode='rb') as f:
        [report_tf, audio_tf, report_tfidf, audio_tfidf, report_word2vec, audio_word2vec, report_doc2vec, audio_doc2vec]=pickle.load(f)
    with open(report_pickle_path, mode='rb') as f:
        [content, section_title, addtion] = pickle.load(f)
        
    with open(audio_pickle_path, mode='rb') as f:
        [sentense_list, s_start_time_list, s_end_time_list, slide_sentense_index] = pickle.load(f)
        
    audio_content = []
    for index_list in slide_sentense_index:
        line = ''
        for index in index_list: line += sentense_list[index]
        audio_content.append(line)
    #####
    
    vector = list(report_tfidf)+list(audio_tfidf)
    max_eps, group = findBestEps(vector)
    N = len(content)
    
    #wordcloudの作成
    wordcloud_path = f'pvis_data/addtion_data/{file_name}/wordcloud'
    os.makedirs(wordcloud_path,exist_ok=True)
    
    for g in group:
        index_list = group[g]
        new_text = ''
        print([c for c in index_list if c<N], [c-N for c in index_list if c>N-1])
        for index in index_list:
            if index < N:new_text += content[index]+' '
            else: new_text += audio_content[index-N]+' '
            
        wc = WordCloud(width=400, height=300, background_color='white')
        wc.generate(new_text)
        wc.to_file(f'{wordcloud_path}/{g}.png')
        
    with open(f'{wordcloud_path}/cluster.pickle', mode='wb') as f:
        pickle.dump([group],f)
        
    
            
        
        