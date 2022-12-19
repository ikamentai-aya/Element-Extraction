import re
import os
import pickle
import statistics
import collections


def arange2Column(path):
    with open(path) as f:
        s = f.read()

    line = s.split('\n')

    max_len = 0
    for l in line:
        if len(l) > max_len: max_len = len(l)

    half_len = max_len//2
    center = []
    right = []
    left = []
    num_pt = re.compile('[0-9]+')
    s_pt = re.compile('\s\s\s\s+')
    
    column_start = False 
    
    start_list = []
    end_list = []
    for l in line:
        s_start = 0
        s_m = s_pt.search(l)
        if s_m!= None:s_start = s_m.start()
        if s_start>10:
            start_list.append(s_start)
            end_list.append(s_m.end())
            
    s = collections.Counter(start_list)
    start = max(s.most_common()[0][0], s.most_common()[1][0])
    e = collections.Counter(end_list)
    kouho = []
    for i in range(min(2, len(e.most_common()))):
        if e.most_common()[i][0] > start:kouho.append(e.most_common()[i][0])
            
    end = min(kouho)
    
    
    print(start, end)
            
    for l in line:
        s_start = 0
        s_m = s_pt.search(l)
        if s_m!= None:s_start = s_m.start()
        if l == '':continue
        #if 
        if s_start>0 or l[end-5:end]=='     ': #2カラムのとき
            left.append(l[:start+5])
            right.append(l[end:])
            column_start = True
        elif len(l)<end and column_start:
            left.append(l[:start])
            right.append(l[end:])

        else:
            s_free = re.sub('^\s+','',l)
            center.append(re.sub('^[0-9]*','',l))
    return center, left, right

import re

def arangeParagraph(content):
        
    content = [c for c in content if c !='']
    new_content = []
    
    ##最初に段落に分ける
    start_blank = [] #先頭にブランクがいくつあるか
    end_with_comma = [] #カンマで終わるか
    line_length = [] 
    large_count = []
    
    for line in content:
        #文末の空白を削除する
        line= re.sub(r' *$', '', line)
        first_blank = re.match(" *", line).end()
        if first_blank == len(line) or len(line)==0:
            continue
        if first_blank > 10:continue
        
        new_content.append(line)
        start_blank.append(first_blank)
        end_with_comma.append(line[-1]=='.')
        line_length.append(len(line))
        large_count.append(sum(map(str.isupper, line)))
        
    arange_content = []
    for i, line in enumerate(new_content[:-1]):
        arange_content.append(re.sub('^ *', '', line))
        if i==0:continue
        isShort = (line_length[i]+large_count[i]<line_length[i-1])
        nextBlank = (start_blank[i]*2<start_blank[i+1])
        if end_with_comma[i] and (isShort or nextBlank):
            arange_content.append('')
    if new_content!=[]: arange_content.append(new_content[-1])
            
    return arange_content

def arangePage(center, left, right, section_num, pa_num):
    def appendContent(text, new_content, pa_num):
        
        if text != '' and len(text)>20: 
            new_content.append(text)
            pa_num += 1
        return new_content, pa_num
        
    content_center = arangeParagraph(center)
    content_right = arangeParagraph(right)
    content_left = arangeParagraph(left)

    content = content_center + [''] + content_left + ['']+content_right
    isTable = False #現在の内容がTableか
    isFigure = False #現在の内容がFigureか
    
    #セクションタイトルの抽出
    section_pt = re.compile(r'[0-9]+?[\. A-Z].*')
    section_num_pt = re.compile(r'([0-9]+?)[\. A-Z].*')
    
    num_start_pt = re.compile(r'[0-9]+.*')
    
    new_content = []
    section_title = []
    addition = []
    now_text = ''
    #段落ごとに処理
    for index, sentense in enumerate(content):
        isAdd = False
        
        #元から空白行が存在する→
        if sentense == '':
            if isFigure or isTable: addition.append(now_text)
            else: new_content, pa_num = appendContent(now_text,new_content, pa_num)
            now_text = ''
            isTable=False; isFigure=False
            continue    
        
        #セクションタイトルだったら現在の文を追加
        r = section_num_pt.match(sentense)
        if r:
            sec_now = int(r.group(1))
            notHirabun = True
            #もしかしたら文頭に出てきただけの可能性を排除する
            if not('.' in sentense.split()[0]):
                m = re.match(r'[A-Z]', sentense.split()[1][0])
                if not m:notHirabun = False
            
            if (sec_now in [section_num,section_num+1, section_num+2]) and notHirabun: 
                #section番号が現在と同じかそれより一つ上ならこれはセクションタイトル
                print(r.group())
                if now_text != '':
                    if isFigure or isTable: addition.append(now_text)
                    else: new_content, pa_num = appendContent(now_text, new_content, pa_num)
                section_num = sec_now #現在のセクション番号の更新
                section_title.append([r.group(),pa_num])
                now_text = ''
                isFigure=False; isTable=False
                continue

        #セクションタイトルだったら現在の文を追加
        r = re.match(r'[A-Z]+', sentense)
        if r:
            if r.group() == sentense:
                if now_text != '':
                    if isFigure or isTable: addition.append(now_text)
                    else: new_content, pa_num = appendContent(now_text, new_content, pa_num)
                section_title.append([r.group(),pa_num])
                now_text = ''
                isFigure=False; isTable=False
                continue
            
        sentense = re.sub(r'\s\s+', '', sentense)    
           
        #FigやTABLEから始まる時
        #複数行になるかもしれないので保留
        if ('Figure' in sentense[:6] or 'TABLE' in sentense[:6] or 'Table' in sentense[:6]) and  ':' in sentense[:10] :
            print(sentense)
            #その前の段落はコンテントに入れる
            if now_text != '': new_content, pa_num = appendContent(now_text, new_content, pa_num)
            
            if 'Table' in sentense[:6]:
                isTable=True
                isFigure=False
            else:
                isTable=False
                isFigure=True
            now_text = sentense
            continue
        
        #現在の内容が表の中身かどうかの確認
        if isTable:
            new_sentense = re.sub('[0-9]+\.[0-9]+', '', sentense)
            if not '.' in new_sentense:continue
                
        now_text += sentense + ' '  
    
    new_content, pa_num = appendContent(now_text,new_content, pa_num)

    return new_content, section_title, addition, section_num, pa_num

def deriveReport(paper_path):
    output_path = 'pvis_data/addtion_data'
    paper_name = paper_path.split('/')[-1].split('.')[0]
    
    ##ページ数の取り出し
    
    path = f'{output_path}/{paper_name}/report_content/metadata'
    f = open(path, 'w')
    f.write('')  # 何も書き込まなくてファイルは作成されました
    f.close()
    
    os.system(f'pdfinfo {paper_path} > {output_path}/{paper_name}/report_content/metadata')
    with open(f'{output_path}/{paper_name}/report_content/metadata') as f:
        l = f.readlines()
    nums_pt = re.compile('[0-9]+')
    for line in l:
        if 'Pages' in line:
            num = int(nums_pt.findall(line)[0])
    #いらなくなったファイルを削除
    os.system(f'rm {output_path}/{paper_name}/report_content/metadata')

    #各ページの読み取り結果をファイルに保存
    for i in range(1,num+1):
        os.system(f'pdftotext -f {i} -l {i} -layout {paper_path} {output_path}/{paper_name}/report_content/{i}.txt')

    ##実際に読み取りを行う
    pa_num = 0
    section_num = 1
    content = []
    section_title = []
    addtion = []
    for i in range(1,num+1):
        center, left, right = arange2Column(f'{output_path}/{paper_name}/report_content/{i}.txt')
        new_content, new_section_title, new_addition, section_num, pa_num = arangePage(center, left, right, section_num, pa_num)
        content += new_content
        section_title += new_section_title
        addtion += new_addition
        
    #referenceの削除
    cut_index = len(content)
    for index, c in enumerate(content):
        if c.replace(' ', '').startswith('REFERENCE'):cut_index=index
            

    save_path = f'{output_path}/{paper_name}/report_content/content.pickle'
    if os.path.exists(save_path): os.remove(save_path)
    #結果の保存
    with open(save_path, mode='wb') as f:
        pickle.dump([content[:cut_index], section_title, addtion], f)
        
    ## 引用リストの保存
    cite_part = ' '.join(content[cut_index:])
    cite_list = cite_part.split('[')
    cite_dict = dict()
    cite_pt = re.compile('([0-9]+)\](.*)')
    
    for cite in cite_list:
        a = cite_pt.match(cite)
        if a: cite_dict[a.group(1)] = a.group(2)
    ## 引用の内容の保存
    save_path = f'{output_path}/{paper_name}/report_content/cite.pickle'
    with open(save_path, mode='wb') as f:
        pickle.dump([cite_dict], f)
