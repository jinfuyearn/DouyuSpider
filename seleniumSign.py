# selenium js 签名
from selenium import webdriver
import time
import requests
import json

print('init selenium')
driver = webdriver.Chrome()

deviceId = '1cebd38f0e9643024ff4406700071501'
acf_auth = '4d7e0P7bPvIuW9kx5AFjqblympFlgadDdRbgBzIo%2Fl%2BjbSQdHD%2Bn%2F9IVpgQgrr1NPX2Dhsnl9FWE3PXCJOmpxMRHuWU7Nf' \
           '%2FCSdyR5enhClp%2Bsof05U4r'


def get_m3u8_url(hash_id, point_id):
    url = 'https://v.douyu.com/show/' + hash_id
    print('selenium opening url: ' + url)
    driver.get(url)
    get_stream_url = 'https://v.douyu.com/api/stream/getStreamUrl'
    timestamp = str(int(time.time()))
    # 调用js
    js_sign_result = driver.execute_script(
        "return ub98484234('" + point_id + "','" + deviceId + "','" + timestamp + "');")
    # 关闭标签页
    # driver.close()
    data = js_sign_result + "&vid=" + hash_id
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    cookies = {'dy_did': deviceId, 'acf_auth': acf_auth}
    stream_url_json = json.loads(requests.post(get_stream_url, data=data, headers=headers, cookies=cookies).text)
    # get the best quality m3u8 video url
    best_m3u8_url = ''
    thumb_video = stream_url_json['data']['thumb_video']
    if 'normal' in thumb_video and thumb_video['normal'] != '':
        best_m3u8_url = thumb_video['normal']['url']
    if 'high' in thumb_video and thumb_video['high'] != '':
        best_m3u8_url = thumb_video['high']['url']
    if 'super' in thumb_video and thumb_video['super'] != '':
        best_m3u8_url = thumb_video['super']['url']
    return best_m3u8_url
