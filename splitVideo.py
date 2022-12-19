import cv2
from os import makedirs
from os.path import splitext, dirname, basename, join


#path = input()

def save_frames(video_path, frame_dir, second, name="image", ext="jpg"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    
    #静止画のファイル名を決めている
    v_name = splitext(basename(video_path))[0]
    if frame_dir[-1:] == "\\" or frame_dir[-1:] == "/":
        frame_dir = dirname(frame_dir)
    frame_dir_ = join(frame_dir, v_name)

    makedirs(frame_dir_, exist_ok=True)
    base_path = join(frame_dir_, name)

    
    idx = 0
    
    one_frame = cap.get(cv2.CAP_PROP_FPS)
    # 29.97002997002997

    max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # 360.0
    
    num = 0
    for f in range(0, int(max_frame), int(one_frame)*second):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ret, frame = cap.read()
        filled_num = str(num).zfill(4)

        if ret:
            cv2.imwrite("{}_{}.{}".format(base_path, filled_num, ext), frame)
        num+=1
        if num%100==0:print(num)
    return frame_dir_
        

def splitVideo(path, second):
    file_name = path.split('/')[-1].split('.')[0]
    save_path = f'pvis_data/addtion_data/{file_name}/video_content'
    path = save_frames(path, save_path, second)
    return path