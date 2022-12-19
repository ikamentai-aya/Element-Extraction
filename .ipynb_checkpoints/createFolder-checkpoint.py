#最初にフォルダー関連のいろんなことをしてくれる関数
import shutil
import os

def createFolder(file_name):
    output_path = f'pvis_data/addtion_data/{file_name}'
    #paper_name = paper_path.split('/')[-1].split('.')[0]

    os.system(f'mkdir -p {output_path}')
    os.system(f'mkdir -p {output_path}/report_content')
    os.system(f'mkdir -p {output_path}/previews')
    
    #必要なデータを全て移行する
    pdf_path = f'session8/pdf/{file_name}.pdf'
    presen_path = f'session8/presentations/{file_name}.mp4'
    supplemental_path = f'session8/previews/{file_name}.mp4'
    
    shutil.copyfile(pdf_path, f'{output_path}/{file_name}.pdf')
    shutil.copyfile(presen_path, f'{output_path}/{file_name}.mp4')
    shutil.copyfile(supplemental_path, f'{output_path}/previews/{file_name}.mp4')
    
    

