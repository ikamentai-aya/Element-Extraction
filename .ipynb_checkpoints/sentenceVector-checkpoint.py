####それぞれ、スライドの段落と音声をベクトルかしていく####
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from wordcloud import WordCloud

def TFIDFfilter(corpus):
    ##TFIDFの計算
    vectorizer = TfidfVectorizer(stop_words='english', use_idf=True)
    vectorizer.fit(corpus)
    X = vectorizer.transform(corpus)
    X = X.toarray()
    
    #TFIDFのラベル,idfを獲得
    label = vectorizer.get_feature_names_out()
    idf = vectorizer.idf_
    
    #TFIDFのトップ20単語のTFを計算
    #word2vecの平均を計算
    tf_array = []
    word2vec_array = []
    vector_n = len(X[0])
    top_label_list = []
    
    for x_index, x in enumerate(X):
        n_array = [0 for i in x]
        sort_x, sort_index = zip(*sorted(zip(x, list(range(vector_n)))))
        
        count = 0
        sort_i = 0
        reverse_sort_index = sort_index[::-1]
        while count <= 20:
            i = reverse_sort_index[sort_i]
            n_array[i] = corpus[x_index].count(label[i])
            count += 1; sort_i += 1
        tf_array.append(n_array)
        top_label = [label[i] for i in sort_index[::-1][:20]] 
        top_label_list.append(' '.join(top_label))
        
    return tf_array, top_label_list, X
    
    
####メイン関数####
def catchContent(file_name):
    
    report_pickle_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    audio_pickle_path = f'pvis_data/addtion_data/{file_name}/video_content/slide_audio.pickle'
    
    ###データの読み込み###
    with open(report_pickle_path, mode='rb') as f:
        [content, section_title, addtion] = pickle.load(f)
    
    with open(audio_pickle_path, mode='rb') as f:
        [sentense_list, s_start_time_list, s_end_time_list, slide_sentense_index] = pickle.load(f)
        
    audio_content = []
    for index_list in slide_sentense_index:
        line = ''
        for index in index_list: line += sentense_list[index]
        audio_content.append(line)
        
    ###個数###
    report_n = len(content)
    audio_n = len(audio_content)
    corpus=content+audio_content
    
    ####doc2vecの作成####
    model = Doc2Vec.load('code_data/doc2vec.model')
    report_doc2vec = []
    for line in content:
        vector = model.infer_vector(line.lower().split())
        report_doc2vec.append(vector)
        
    audio_doc2vec = []
    for line in audio_content:
        vector = model.infer_vector(line.lower().split())
        audio_doc2vec.append(vector)
    print(len(report_doc2vec),len(audio_doc2vec))
    
    ####TFIDFの作成#####
    tf_array, top_label_list, X = TFIDFfilter(corpus)
    report_tf = tf_array[:report_n]
    audio_tf = tf_array[report_n:]
    report_tfidf = X[:report_n]
    audio_tfidf = X[report_n:]
    
    word2vec = []
    
    for label_list in top_label_list:
        vector = np.zeros(50)
        count = 0
        for word in label_list.split():
            if word in model.wv:
                vector += model.wv[word]
                count+=1
        vector = vector/count
        word2vec.append(vector)
    report_word2vec = word2vec[:report_n]
    audio_word2vec = word2vec[report_n:]
        
    save_path = f'pvis_data/addtion_data/{file_name}/vector.pickle'
    with open(save_path, mode='wb') as f:
        pickle.dump([report_tf, audio_tf, report_tfidf, audio_tfidf, report_word2vec, audio_word2vec, report_doc2vec, audio_doc2vec], f)
        
def createWordCloudAbstarct(file_name):
    report_pickle_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    
    ###データの読み込み###
    with open(report_pickle_path, mode='rb') as f:
        [content, section_title, addtion] = pickle.load(f)
    
    #wordcloudの作成
    text = ' '.join(content)
    wc = WordCloud(width=400, height=300, background_color='white', font_path='~/System/Library/Fonts/HelveticaNeue.ttc')
    result = wc.generate(text).layout_
    wc.to_file(f'pvis_data/addtion_data/{file_name}/wordcloud.jpg')
    
    #abstractの作成
    abstract = ''
    for c in content:
        if 'abstract' in c.replace(' ','').lower():
            abstract = c
            break
            
    if abstract != '':
        abstract_list = abstract.split('*')
        for ab in abstract_list:
            if 'A BSTRACT' in ab:
                abstract = ab.replace('A BSTRACT','')
        with open(f'pvis_data/addtion_data/{file_name}/abstract.txt', mode='w') as f:
            f.write(abstract)
    