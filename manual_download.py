import requests
import os
import shutil


def download(m3u8_url, part, file_path):
    real_url = m3u8_url % part
    try:
        resp = requests.get(real_url)
    except requests.exceptions.ConnectionError:
        print('request [%s] failed' % part)
        return 1
    file_name = os.path.join(file_path, '%s.ts' % part)
    with open(file_name, 'wb') as f:
        f.write(resp.content)
    with open('tsFileList.txt', 'a') as f:
        abs_path = os.path.join(os.getcwd(), file_name)
        f.write('file \'%s\'' % abs_path + '\n')
    return 0


def main():
    url = 'https://play-tx-recpub.douyucdn2.cn/live/high_live-19223rqAUCIibPCy--20180801180155' \
          '/32bee38beb5a43ff951745e832edb32c_0000%s.ts?tlink=61a1c81d&tplay=61a254bd&exper=0&nlimit=5&us' \
          '=8cd5db3dc55baf6ea2a78acc00031601&sign=78d53849bcdd179a824afa3c54ce5e9b&u=0&d' \
          '=8cd5db3dc55baf6ea2a78acc00031601&ct=&vid=5298050&pt=2&cdn=tx'
    # url = 'https://play-tx-recpub.douyucdn2.cn/live/high_live-19223rqAUCIibPCy--20180801200156' \
    #       '/64f37fe69c1742759899bda4adc2500f_0000%s.ts?tlink=61a1fb3e&tplay=61a287de&exper=0&nlimit=5&us' \
    #       '=8cd5db3dc55baf6ea2a78acc00031601&sign=2b3bfeb160bfbddbccd841781265cdaa&u=0&d' \
    #       '=8cd5db3dc55baf6ea2a78acc00031601&ct=&vid=5301255&pt=2&cdn=tx'
    start = 685
    stop = 720
    timestamp = '2018080101'

    temp = 'temp_%s' % timestamp
    if not os.path.exists(temp):
        os.mkdir(temp)
    for i in range(start, stop + 1):
        part = '%03d' % i
        cnt = 0
        while download(url, part, temp):
            if cnt >= 5:
                print('retry max times, exit')
                return
            cnt += 1

    if not os.path.exists(timestamp):
        os.mkdir(timestamp)
    tmp_file = os.path.join(temp, '*.ts')
    video_file = os.path.join(timestamp, '%s.ts' % timestamp)
    cmd = 'copy /b %s %s' % (tmp_file, video_file)
    print(cmd)
    os.system(cmd)
    mp4_file = os.path.join(timestamp, '%s.mp4' % timestamp)
    cmd = 'ffmpeg -f concat -safe 0 -i tsFileList.txt -acodec copy -vcodec copy -absf aac_adtstoasc %s' % mp4_file
    print(cmd)
    os.system(cmd)
    shutil.rmtree(temp)
    os.remove('tsFileList.txt')
    print('done')


if __name__ == '__main__':
    main()
    # 手动转mp4文件：ffmpeg -i "concat:2018080101\2018080101.ts|2018080102\2018080102.ts|" -acodec copy -vcodec copy
    # -absf aac_adtstoasc 20180801\20180801.mp4
