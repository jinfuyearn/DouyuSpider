# m3u8下载器
import os
import threading

import requests
import time


# 获取基地址
def get_base_url(m3u8_url):
    # 从最后一个 / 开始算
    # 问号索引
    question_mark_index = m3u8_url.index('?')
    # 斜杠索引
    slash_index = question_mark_index - 1
    while m3u8_url[slash_index] != '/' and slash_index >= 0:
        slash_index = slash_index - 1
    return m3u8_url[0:slash_index + 1]


# 发请求获取m3u8碎片列表
def get_piece_url_list(base_url, m3u8_url, piece_cache_path):
    m3u8_file = requests.get(m3u8_url).text
    # 保存m3u8文件
    # with open(pieceCachePath + '/playlist.m3u8', 'w') as playlistFile:
    #     code.write(playlistFile)
    #     playlistFile.flush()
    lines = m3u8_file.splitlines()
    piece_url_list = []
    # 保存文件列表
    ts_file_list = open(piece_cache_path + '/ts_file_list.txt', 'w')
    # 遍历每一行
    for line in lines:
        # 不以#开头，并且不是空行
        if not line.startswith('#') and line != '':
            piece_url_list.append(base_url + line)
            ts_file_list.write("file '" + line[0:line.index('?')] + '\'\n')
            ts_file_list.flush()
    return piece_url_list


# 碎片数量
pieceAmount = 0
# 碎片缓存文件夹路径
pieceCachePath = ''
# 最终文件路径
finalFilePath = ''


# 创建缓存文件夹，保存所有碎片
def get_piece_cache_path(save_path, folder_name):
    if save_path.endswith('/'):
        piece_cache_path = save_path + folder_name
    else:
        piece_cache_path = save_path + '/' + folder_name
    if not os.path.exists(piece_cache_path):
        os.makedirs(piece_cache_path)
    return piece_cache_path


# 下载一个文件
def download_single_file(url, path):
    try:
        r = requests.get(url)
        with open(path, 'wb') as code:
            code.write(r.content)
            code.flush()
    except requests.exceptions:
        r = requests.get(url)
        with open(path, 'wb') as code:
            code.write(r.content)
            code.flush()


# 合并碎片
def merge_pieces(f_path, p_cache_path):
    p_amount = len(missionList)
    # 先拿到碎片文件列表
    piece_file_path_list = []
    for i in range(0, p_amount):
        piece_file_path_list.append(p_cache_path + '/' + str(i))
    # 执行合并
    # final_file = open(f_path, 'wb')
    # 遍历每个碎片
    # for pieceFilePath in piece_file_path_list:
    #     with open(pieceFilePath, 'rb') as pieceFile:
    #         current = int(os.path.basename(pieceFilePath)) + 1
    #         total = p_amount
    #         percent = round(current / total * 100, 1)
    #         print('merge piece: ' + str(current) + ' / ' + str(total) + '  ' + str(percent) + '%')
    #         content = pieceFile.read()
    #         final_file.write(content)
    # final_file.close()

    # cmd = 'ffmpeg -y -i \"concat:'
    # for pieceFilePath in piece_file_path_list:
    #     cmd = cmd + pieceFilePath + '|'
    # cmd = cmd + '\" -acodec copy -vcodec copy -absf aac_adtstoasc ' + fPath.replace('\\', '/')
    # print(cmd)
    # os.system(cmd)

    # ffmpeg -i "index.m3u8" -codec copy output.mp4
    cmd = "ffmpeg -y -f concat -i " + p_cache_path + "/\"tsFileList.txt\" -c copy " + f_path
    print(cmd)
    os.system(cmd)

    # 删除碎片
    for mission in missionList:
        ts_path = mission['path']
        os.remove(ts_path)
        print("delete ts piece: " + ts_path)
    # 删除tsFileList文件
    os.remove(p_cache_path + '/tsFileList.txt')
    # 删除缓存文件夹
    os.rmdir(p_cache_path)
    print('merge ts pieces finish')


# 锁
threadLock = threading.Lock()
# 任务列表
# state: 0表示未下载，1表示正在下载，2表示已完成
missionList = []

# 下载进度
progress = {'downloadBytes': 0, 'startTime': 0.0}


def get_progress():
    return progress


# 初始化任务
def init_download_mission(piece_url_list, piece_cache_path):
    progress['downloadBytes'] = 0
    progress['startTime'] = time.time()
    for index, pieceUrl in enumerate(piece_url_list):
        # 这里改一下ts碎片文件名，按照m3u8索引文件里的名字来
        relative_url = pieceUrl.replace(get_base_url(pieceUrl), '')
        filename = relative_url[0:relative_url.index('?')]
        missionList.append({
            'index': index,
            'url': pieceUrl,
            'path': piece_cache_path + '/' + filename,
            'size': 0,
            'state': 0
        })


# 获取任务
def get_piece_mission():
    # 先上锁
    threadLock.acquire()
    # 遍历任务列表
    for mission in missionList:
        # 找到未下载的任务
        if mission['state'] == 0:
            # 标记为正在下载
            mission['state'] = 1
            # 释放锁
            threadLock.release()
            # 返回任务
            return mission
    # 如果走到这了，就说明所有任务都已经完成了
    # 释放锁
    threadLock.release()
    # 返回空
    return None


# 碎片下载完成，提交任务
def submit_mission(mission):
    # 先上锁
    threadLock.acquire()
    # 把对应任务标记为已完成
    missionList[mission['index']]['state'] = 2
    finish_count = 0
    # 遍历mission列表
    for mission in missionList:
        # 统计已经完成的任务数
        if mission['state'] == 2:
            finish_count = finish_count + 1
    # 下载完成度
    percent = round(finish_count / len(missionList) * 100, 1)
    print(str(percent) + '%', end='')
    # 释放锁
    threadLock.release()


# 所有任务已完成
def on_all_missions_finished():
    print('onAllMissionsFinished')
    # mergePieces()
    # 开启新线程合并碎片
    # _thread.start_new_thread(mergePieces,())


# 多线程下载类
class DownloadThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        # 获取任务
        mission = get_piece_mission()
        # 循环接新任务，如果有任务
        while mission is not None:
            # 执行下载
            print(threading.currentThread().getName() + ' downloading ' + str(mission['index']) + " " + mission['path'])
            download_single_file(mission['url'], mission['path'])
            # 设置文件大小，用于统计速度
            mission['size'] = os.path.getsize(mission['path'])
            # 提交任务
            submit_mission(mission)
            # 计算下载速度
            progress_info = get_progress()
            download_bytes = progress_info['download_bytes']
            ts_size = mission['size']
            download_bytes = download_bytes + ts_size
            progress_info['download_bytes'] = download_bytes
            time_cost = time.time() - progress_info['startTime']
            speed = download_bytes / 1024 / time_cost
            # 速度
            print(" " + "\033[1;34;42m " + str(int(speed)) + " K/S \033[0m", end='')
            # ts文件大小
            print("  " + str(int(ts_size / 1024)) + "KB", end='')
            # video已下载总大小
            print("  " + str(int(download_bytes / 1024 / 1024)) + "MB", end='')
            # video耗时
            time_cost_in_second = int(time_cost)
            minute = int(time_cost_in_second / 60)
            second = int(time_cost_in_second % 60)
            print("  " + str(minute) + ":" + str(second))
            # 继续获取新任务
            mission = get_piece_mission()


# 下载视频，m3u8Url，保存路径，最终文件名
def download(m3u8_url, save_path, filename):
    # 文件分隔符替换
    save_path = save_path.replace('\\', '/')
    # 获得碎片缓存文件夹路径
    piece_cache_path = get_piece_cache_path(save_path, filename + '_cache')
    base_url = get_base_url(m3u8_url)
    # 拿到下载文件URL列表
    piece_url_list = get_piece_url_list(base_url, m3u8_url, piece_cache_path)
    # 碎片数量
    # piece_amount = len(piece_url_list)
    # 最终文件路径
    final_file_path = save_path + '/' + filename
    # 开启多线程下载每个碎片
    # 初始化下载任务
    init_download_mission(piece_url_list, piece_cache_path)
    # 线程数量
    thread_amount = 5
    # 线程池
    thread_pool = []
    # 创建线程
    for i in range(thread_amount):
        each_thread = DownloadThread(i, "Thread-" + str(i))
        each_thread.start()
        thread_pool.append(each_thread)
        # 等待所有线程完成
    for t in thread_pool:
        t.join()

    print('------thread finish------')
    merge_pieces(final_file_path, piece_cache_path)
    # piece_amount = 0
    # piece_cache_path = ''
    # final_file_path = ''
    missionList.clear()
