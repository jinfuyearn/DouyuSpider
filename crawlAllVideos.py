import requests
import json
import math
import db
import datetime

# https://v.douyu.com/author/0rEdlk3MgwNM

# https://v.douyu.com/wgapi/vod/center/getAuthorShowAndVideoList?up_id=0rEdlk3MgwNM&uid=2954707&page=1&limit=3&type=0
# https://v.douyu.com/wgapi/vod/center/getAuthorShowVideoList?up_id=0rEdlk3MgwNM&uid=2954707&page=6&limit=5&show_id=165675506&type=0

# 爬取所有的视频信息，并保存
# 一次直播有一个videoShow，按照两小时分为多个video，这些video的日期 可能跨天
# show中的list，包含一次直播所有的videos数组
# 这里的videos可能是直播回放，也可能是精彩时刻，或直播片段
up_id = '0rEdlk3MgwNM'
show_limit = 3
video_limit = 5

# 获取mysql连接
connect = db.get_mysql_connect()
cursor = connect.cursor()


# 获取show信息
def get_show_info(page_id):
    url = 'https://v.douyu.com/wgapi/vod/center/getAuthorShowAndVideoList?up_id=' + up_id + \
          '&page=' + str(page_id) + '&limit=' + str(show_limit) + '&type=0'
    return json.loads(requests.get(url).text)


# 获取video信息
def get_video_info(show_id, page_id):
    url = 'https://v.douyu.com/wgapi/vod/center/getAuthorShowVideoList?up_id=' + up_id \
          + '&page=' + str(page_id) + '&limit=' + str(video_limit) + '&show_id=' + str(show_id) + '&type=0'
    return json.loads(requests.get(url).text)


# 保存一次show所对应的所有videos
def save_videos(show_id, total_video_count):
    # 计算总页数
    total_page = math.ceil(total_video_count / video_limit)
    # 遍历获取每一页
    for page_id in range(1, total_page + 1):
        # 拿到video列表
        video_list = get_video_info(show_id, page_id)['data']
        # 遍历拿到每一个video
        for index_of_show, eachVideo in enumerate(video_list):
            # 根据hash_id查询数据库，判断是video是否已经存在
            # 查询某个期间所有订单数（已支付+未支付）
            sql_count = "select count(*) from douyu_video where hash_id='" + eachVideo['hash_id'] + "'"
            cursor.execute(sql_count)
            connect.commit()
            count_hash_id = cursor.fetchall()[0][0]
            # 如果不存在，则保存
            if count_hash_id == 0:
                sql = "INSERT INTO douyu_video(up_id,show_id,index_of_show,title,video_type," \
                      + "start_time,hash_id,video_str_duration,point_id,json,video_page,video_limit," \
                        "is_download,create_time)" \
                      + "VALUES('%s','%s',%d,'%s',%d,'%s','%s','%s','%s','%s',%d,%d,%d,'%s')"
                data = (up_id, show_id, index_of_show, eachVideo['title'], eachVideo['video_type'],
                        eachVideo['start_time'], eachVideo['hash_id'], eachVideo['video_str_duration'],
                        eachVideo['point_id'], json.dumps(eachVideo), page_id, video_limit, 0,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                cursor.execute(sql % data)
                connect.commit()
                print('save a video:  hash_id = ' + eachVideo['hash_id'] + ', pointId = '
                      + str(eachVideo['point_id']) + ', title = ' + eachVideo['title'])
            else:
                # 如果已经存在，跳过
                print("video已存在 skip " + eachVideo['hash_id'] + " " + eachVideo['title'])


# 保存show和video
def save_shows_and_videos(show_list, up_id, page_id):
    for eachShow in show_list:
        # 拿第一个video，解析出本场直播开始时间
        start_timestamp = eachShow['video_list'][0]['start_time']
        start_date_time = datetime.datetime.utcfromtimestamp(start_timestamp)
        # 斗鱼这里有bug，可能会，出现startTime是零，mysql比较奇葩，1970不能插入，必须全零
        if start_timestamp != 0:
            start_year = start_date_time.year
            start_month = start_date_time.month
            start_day = start_date_time.day
        else:
            start_year = 0
            start_month = 0
            start_day = 0
        # 先根据show_id查询数据库，看该场show是否已经存在
        sql_count = "select count(*) from douyu_show where show_id='" + str(eachShow['show_id']) + "'"
        cursor.execute(sql_count)
        connect.commit()
        count_hash_id = cursor.fetchall()[0][0]
        # 如果不存在，则保存
        if count_hash_id == 0:
            sql = "INSERT INTO douyu_show(up_id,show_id,start_time,title,cut_num,fan_num," \
                  + "re_num,show_page,show_limit,start_timestamp,start_year,start_month,start_day," \
                    "is_reply_download,create_time)" \
                  + "VALUES('%s','%s','%s','%s',%d,%d,%d,%d,%d,'%s',%d,%d,%d,%d,'%s')"
            if start_timestamp != 0:
                data = (up_id, eachShow['show_id'], eachShow['time'], eachShow['title'], eachShow['cut_num'],
                        eachShow['fan_num'], eachShow['re_num'], page_id, show_limit,
                        start_date_time.strftime("%Y-%m-%d %H:%M:%S"), start_year, start_month, start_day, 0,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                data = (up_id, eachShow['show_id'], eachShow['time'], eachShow['title'], eachShow['cut_num'],
                        eachShow['fan_num'], eachShow['re_num'], page_id, show_limit,
                        '0000-00-00 00:00:00', start_year, start_month, start_day, 0,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(sql % data)
            connect.commit()
            print('save a show: ' + 'page = ' + str(page_id) + ', show_id = ' + str(eachShow['show_id'])
                  + ' ,title = ' + eachShow['title'])
        else:
            # 如果show不存在
            print("show已存在，skip " + str(eachShow['show_id']) + " " + eachShow['title'])
        total_video_count = eachShow['cut_num'] + eachShow['fan_num'] + eachShow['re_num']
        # show就算是已经保存了，还是要保存video，因为可能有任务中途中断，video也会自己判断是否存在
        save_videos(eachShow['show_id'], total_video_count)


if __name__ == '__main__':
    # 先发一个请求，拿到count总数
    firstVideoShow = get_show_info(1)
    count = firstVideoShow['data']['count']
    # 计算总页数
    totalPage = math.ceil(count / show_limit)
    # 遍历每一页，发请求，保存videoInfo
    for page in range(330, totalPage + 1):
        videoShowList = get_show_info(page)['data']['list']
        save_shows_and_videos(videoShowList, up_id, page)
