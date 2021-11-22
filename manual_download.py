import requests
import os

url = 'https://play-tx-recpub.douyucdn2.cn/live/super_live-7261911rcjksRSiB--20211102155530/transcode_live' \
      '-7261911rcjksRSiB--20211102155530_128441_0000%s.ts?tlink=61824e31&tplay=6182dad1&exper=0&nlimit=5&us' \
      '=77b76c28d3bf8fba279062bc14357d3d&sign=9b6e2ffef900064a50835762492458ee&u=0&d=77b76c28d3bf8fba279062bc14357d3d' \
      '&ct=&vid=25801156&pt=1&cdn=tx '


def download(url1, ints):
    urls = url1 % ints
    r = requests.get(urls)  # create HTTP response object
    name = ints + '.ts'
    with open(name, 'wb') as f:
        f.write(r.content)


start = 0
stop = input('结束断点：')
stop = int(stop)

for i in range(start, stop):
    i = str(i)
    if len(i) < 2:
        i = '00' + i
    elif len(i) < 3:
        i = '0' + i
    else:
        pass
    download(url, i)
os.system('copy /b *.ts new1.ts')  # new1.ts是生成的合并后的ts文件
