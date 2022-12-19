import pickle
import graphviz 
import math
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
    
#Wordcloudの結果の利用
def useWordCloudAPI(text_list):
    text = ' '.join(text_list)
    wordcloud = WordCloud()
    wordcloud.generate(text)
    
    return wordcloud.words_

#TFIDFの作成
def createTFIDF(s_list1, s_list2):
    s_list = s_list1+s_list2
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(s_list)
    return X.toarray(), vectorizer.get_feature_names_out()

###クラスター番号を渡すと頻出単語を表示してくれる###
def extractKeyWord(cluster_num, content,audio_content,group):
    s_list = []
    for s in content+audio_content:
        s_list+=s.split('.')
    tfidf,feature_names = createTFIDF(content, audio_content)
    
    cluster_index = group[cluster_num]
    word_set = set()
    for i in cluster_index:
        sort_tfidf, sort_index = zip(*sorted(zip(tfidf[i], range(len(tfidf[i])))))
        sort_index = sort_index[::-1]
        key = [feature_names[j] for j in sort_index[:20]]
        word_set = set(key)|word_set
    
    cloud_words = list(useWordCloudAPI(s_list).keys())
    word_set = list(word_set|set(cloud_words))
    
    s = ' '.join(content+audio_content).replace('.',' ').replace(',',' ').split(' ')
    count = [s.count(word) for word in word_set]
    sort_count,sort_index = zip(*sorted(zip(count, range(len(count)))))
    sort_count,sort_index = sort_count[::-1],sort_index[::-1]
    new_count, new_word_set = [],[]
    
    ##出現回数が２回以上のものだけ採用する##
    w_num = 0
    for i in sort_index:
        if w_num > 50:break
        if count[i]>1:
            new_count.append(count[i])
            new_word_set.append(word_set[i])
            w_num += 1
            
    ##共出現を見つける##
    pair_list = set()
    for i in s_list:
        for j in new_word_set:
            for k in new_word_set:
                if (j in i) and (k in i) and j!=k:pair_list.add(f'{k}-{j}')
    pair_list = [p.split('-') for p in pair_list]
    return new_count, new_word_set, pair_list
    
# graphvizを使ってレイアウトの計算を行う
def createGraph(count, word_set, pair_list,file_name, cluster_num):
    new_count = [c//2+10 for c in count]
    dot = graphviz.Digraph(format='svg',graph_attr={'size':"400,600"})
    dot.engine= 'fdp'
    
    for i,word in enumerate(word_set):
        dot.node(word, fontsize=f"{new_count[i]}pt", shape="box", color="white")
    for [i,j] in pair_list:
        dot.edge(i, j, style="invis")
        
    save_path =f'pvis_data/addtion_data/{file_name}/wordcloud/svg/{cluster_num}'
    dot.render(save_path)
    return save_path
    
# このモジュールのメイン関数
def createWordCloud(file_name):
    ###段落の内容の取得###
    report_pickle_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    audio_pickle_path = f'pvis_data/addtion_data/{file_name}/video_content/slide_audio.pickle'
    with open(report_pickle_path, mode='rb') as f:
        [content, section_title, addtion] = pickle.load(f)
    with open(audio_pickle_path, mode='rb') as f:
        [sentense_list, s_start_time_list, s_end_time_list, slide_sentense_index] = pickle.load(f) 

    ###文字起こしの調整###
    audio_content = []
    for index_list in slide_sentense_index:
        line = ''
        for index in index_list: line += sentense_list[index]
        audio_content.append(line)

    ###クラスタリング結果の取得###
    cluster_path = f'pvis_data/addtion_data/{file_name}/wordcloud/cluster.pickle'
    with open(cluster_path, mode='rb') as f:
        [group] = pickle.load(f)
    
    ## クラスターごとにWordCloudの計算を行い、svg形式で保存する
    for cluster_num in group:
        count, word_set, pair_list = extractKeyWord(cluster_num,content,audio_content,group)
        save_path = createGraph(count, word_set, pair_list,file_name, cluster_num)