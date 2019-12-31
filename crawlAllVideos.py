import requests
import json
import math
import db
import time
import datetime

# https://v.douyu.com/wgapi/vod/center/getAuthorShowAndVideoList?up_id=0rEdlk3MgwNM&uid=2954707&page=1&limit=3&type=0
# https://v.douyu.com/wgapi/vod/center/getAuthorShowVideoList?up_id=0rEdlk3MgwNM&uid=2954707&page=6&limit=5&show_id=165675506&type=0

# 爬取所有的视频信息，并保存
# 一次直播有一个videoShow，按照两小时分为多个video，这些video的日期 可能跨天
# show中的list，包含一次直播所有的videos数组
# 这里的videos可能是直播回放，也可能是精彩时刻，或直播片段
upId = '0rEdlk3MgwNM'
showLimit = 3
videoLimit = 5

# 获取mysql连接
connect = db.getMysqlConnect()
cursor = connect.cursor()


# 获取show信息
def getShowInfo(page):
    url = 'https://v.douyu.com/wgapi/vod/center/getAuthorShowAndVideoList?up_id=' + upId + \
          '&page=' + str(page) + '&limit=' + str(showLimit) + '&type=0'
    return json.loads(requests.get(url).text)


# 获取video信息
def getVideoInfo(show_id, page):
    url = 'https://v.douyu.com/wgapi/vod/center/getAuthorShowVideoList?up_id=' + upId \
          + '&page=' + str(page) + '&limit=' + str(videoLimit) + '&show_id=' + str(show_id) + '&type=0'
    return json.loads(requests.get(url).text)


# 保存一次show所对应的所有videos
def saveVideos(show_id, totalVideoCount):
    # 计算总页数
    totalPage = math.ceil(totalVideoCount / videoLimit)
    # 遍历获取每一页
    for page in range(1, totalPage + 1):
        # 拿到video列表
        videoList = getVideoInfo(show_id, page)['data']
        # 遍历拿到每一个video，并保存
        for indexOfShow, eachVideo in enumerate(videoList):
            sql = "INSERT INTO douyu_video(upId,show_id,indexOfShow,title,video_type," \
                  + "start_time,hash_id,video_str_duration,point_id,json,videoPage,videoLimit," \
                    "isDownload,createTime)" \
                  + "VALUES('%s','%s',%d,'%s',%d,'%s','%s','%s','%s','%s',%d,%d,%d,'%s')"
            data = (upId, show_id, indexOfShow, eachVideo['title'], eachVideo['video_type'],
                    eachVideo['start_time'], eachVideo['hash_id'], eachVideo['video_str_duration'],
                    eachVideo['point_id'], json.dumps(eachVideo), page, videoLimit, 0,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(sql % data)
            connect.commit()
            print('save a video:  hash_id = ' + eachVideo['hash_id'] + ', pointId = '
                  + str(eachVideo['point_id']) + ', title = ' + eachVideo['title'])


# 保存show和video
def saveShowsAndVideos(showList, upId, page):
    for eachShow in showList:
        # 拿第一个video，解析出本场直播开始时间
        startTimestamp = eachShow['video_list'][0]['start_time']
        startDateTime = datetime.datetime.utcfromtimestamp(startTimestamp)
        startYear = startDateTime.year
        startMonth = startDateTime.month
        startDay = startDateTime.day
        sql = "INSERT INTO douyu_show(upId,show_id,start_time,title,cut_num,fan_num," \
              + "re_num,showPage,showLimit,startTimestamp,startYear,startMonth,startDay," \
                "isReplyDownload,createTime)" \
              + "VALUES('%s','%s','%s','%s',%d,%d,%d,%d,%d,'%s',%d,%d,%d,%d,'%s')"
        data = (upId, eachShow['show_id'], eachShow['time'], eachShow['title'], eachShow['cut_num'],
                eachShow['fan_num'], eachShow['re_num'], page, showLimit,
                startDateTime.strftime("%Y-%m-%d %H:%M:%S"), startYear, startMonth, startDay, 0,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cursor.execute(sql % data)
        connect.commit()
        print('save a show: ' + 'page = ' + str(page) + ', show_id = ' + str(eachShow['show_id'])
              + ' ,title = ' + eachShow['title'])
        totalVideoCount = eachShow['cut_num'] + eachShow['fan_num'] + eachShow['re_num']
        saveVideos(eachShow['show_id'], totalVideoCount)


# 先发一个请求，拿到count总数
firstVideoShow = getShowInfo(1)
count = firstVideoShow['data']['count']
# 计算总页数
totalPage = math.ceil(count / showLimit)
# 遍历每一页，发请求，保存videoInfo
for page in range(1, totalPage + 1):
    videoShowList = getShowInfo(page)['data']['list']
    saveShowsAndVideos(videoShowList, upId, page)