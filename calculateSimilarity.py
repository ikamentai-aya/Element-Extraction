from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
import os

def createTFIDF(s_list1, s_list2):
    s_list = s_list1+s_list2
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(s_list)

    return X[:len(s_list1)].toarray(), X[len(s_list1):].toarray()

def cos_similarity(v1,v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def list_cos_similarity(v_list1,v_list2):
    similarity = []
    for v1 in v_list1:
        sim = []
        for v2 in v_list2:
            if np.linalg.norm(v1)==0 or np.linalg.norm(v2)==0:
                sim.append(0)
            else: sim.append(round(cos_similarity(v1,v2),2))
        similarity.append(sim)
    return similarity

###各スライドに対する段落の類似度を計算####

def calculateSimilarity(vector_path, report_pickle_path, audio_pickle_path):
    
    #report_pickle_path = f'pvis_data/addtion_data/{file_name}/report_content/content.pickle'
    #audio_pickle_path = f'pvis_data/addtion_data/{file_name}/video_content/slide_audio.pickle'
    #vector_path = f'pvis_data/addtion_data/{file_name}/vector.pickle'

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

    with open(vector_path, mode='rb') as f:
        [report_tf, audio_tf, report_tfidf, audio_tfidf, report_word2vec, audio_word2vec, report_doc2vec, audio_doc2vec]=pickle.load(f)

    sim_matrix1=list_cos_similarity(report_tf,audio_tf)
    sim_matrix2=list_cos_similarity(report_tfidf,audio_tfidf)
    sim_matrix3=list_cos_similarity(report_word2vec,audio_word2vec)
    sim_matrix4=list_cos_similarity(report_doc2vec,audio_doc2vec)
    p_p_sim_matrix=list_cos_similarity(report_tfidf,report_tfidf)
    
    sim_data = []
    for audio_index, audio in enumerate(audio_content):
        new_sim = []
        for report_index, report in enumerate(content):
            youso = {
                'content':report,
                'tf':sim_matrix1[report_index][audio_index],
                'tfidf':sim_matrix2[report_index][audio_index],
                'word2vec':sim_matrix3[report_index][audio_index],
                'doc2vec':sim_matrix4[report_index][audio_index]
            }
            new_sim.append(youso)
        sim_data.append(new_sim)
        
    save_path = os.path.commonprefix([vector_path, report_pickle_path, audio_pickle_path])+'report_audio_sim.pickle'
    with open(save_path, mode='wb') as f:
        pickle.dump([sim_data], f)
    save_path = os.path.commonprefix([vector_path, report_pickle_path, audio_pickle_path])+'report_sim.pickle'
    with open(save_path, mode='wb') as f:
        pickle.dump([p_p_sim_matrix], f)
        