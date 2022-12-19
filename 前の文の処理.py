import re
import os
import pickle


#各ページごとに文末処理、図表番号の取り出しを行う
def arangePage(page_path, section_num, pa_num):
    
    #with open(page_path, encoding="Shift-JIS") as f:
    with open(page_path) as f:
        content = f.read()
        
    content = content.split('\n\n')[:-1]
    content = [c.replace('\n', ' ') for c in content]
    isTable = False #現在の内容がTableか
    
    #セクションタイトルの抽出
    section_pt = re.compile(r'[0-9]+?[\. ].*')
    section_num_pt = re.compile(r'([0-9]+?)[\. ].*')
    
    num_start_pt = re.compile(r'[0-9]+.*')
    
    new_content = []
    section_title = []
    addition = []
    
    #段落ごとに処理
    for sentense in content:
        
        if sentense in ['', '\n']:continue
        
        #セクションタイトルか確認
        r = section_num_pt.match(sentense)
        if r:
            sec_now = int(r.group(1))
            if sec_now in [section_num,section_num+1]: #section番号が現在と同じかそれより一つ上
                section_num = sec_now #現在のセクション番号の更新
                section_title.append([r.group(),pa_num])
                isTable=False
                continue
        
        #FigやTABLEの除去
        if 'Fig' in sentense[:6] or 'TABLE' in sentense[:6] or 'Table' in sentense[:6]:
            addition.append([sentense, pa_num])
            isTable=False
            if 'Table' in sentense[:6]:isTable=True
            new_sentense=''
            continue
        
        #現在の内容が表の中身かどうかの確認
        if isTable:
            new_sentense = re.sub('[0-9]+\.[0-9]+', '', sentense)
            if not '.' in new_sentense:continue
        
        new_content.append(sentense)
        pa_num+=1
                
    return new_content, section_title, addition, section_num, pa_num


def deriveReport(paper_path):
    output_path = 'pvis_data/addtion_data'
    paper_name = paper_path.split('/')[-1].split('.')[0]
    
    ##ページ数の取り出し
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
        os.system(f'pdftotext -f {i} -l {i} {paper_path} {output_path}/{paper_name}/report_content/{i}.txt')

    ##実際に読み取りを行う
    pa_num = 0
    section_num = 1
    content = []
    section_title = []
    addtion = []
    for i in range(1,num+1):
        new_content, new_section_title, new_addition, section_num, pa_num = arangePage(f'{output_path}/{paper_name}/report_content/{i}.txt', section_num, pa_num)
        content += new_content
        section_title += new_section_title
        addtion += new_addition

    save_path = f'{output_path}/{paper_name}/report_content/content.pickle'
    if os.path.exists(save_path): os.remove(save_path)
    #結果の保存
    with open(save_path, mode='wb') as f:
        pickle.dump([content, section_title, addtion], f)

#paper_path = input()
#deriveReportContent(paper_path)
