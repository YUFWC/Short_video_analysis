import requests
import re
import hashlib
from urllib.parse import quote
import os
import sys




def encode_uri(uri):
    return quote(uri, safe='/:?=&')

def generate_sign(timestamp, homepage):
    key = 'ce544ff3c4c8'
    homepage_encoded = encode_uri(homepage)
    input_str = f"{timestamp}{homepage_encoded}{key}"
    sign = hashlib.md5(input_str.encode('utf-8')).hexdigest()
    return sign

# 请求头


# 视频解析函数
def parse_video(url_2):
    urlss = "https://api.spapi.cn"
    params = {
        'dplayer-danmaku-color-0': "#fff",
        'dplayer-danmaku-type-0': "0",
        'dplayer-toggle': "on",
        'dplayer-toggle-dan': "on"
    }
    headerss = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }

    resp_cookie = requests.get(urlss, verify=False, headers=headerss)
    set_cookie = resp_cookie.headers.get('Set-Cookie')
    cookies = set_cookie.split(';')
    cookies_1 = str(cookies[2]).split(', ')
    cookies_SPAPIID = cookies_1[-1].strip('')
    print(cookies_SPAPIID)

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        'Accept': "application/json, text/plain, */*",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Content-Type': "application/x-www-form-urlencoded",
        'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        'X-Requested-With': "XMLHttpRequest",
        'Origin': "https://api.spapi.cn ",
        'Sec-Fetch-Dest': "empty",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Site': "same-origin",
        'Priority': "u=0",
        'Cookie': cookies_SPAPIID
    }
    timestamp = 1752669921710  # 使用当前时间戳
    sign = generate_sign(timestamp, url_2)
    print(f"[+] 签名 sign: {sign}")

    url1 = f"https://api.spapi.cn/api/parsing?otype=json&timestamp={timestamp}&sign={sign}"

    data = f"url={url_2}"

    try:
        resp = requests.post(url1, data=data, headers=headers, verify=False)
        if resp.status_code == 200:
            result = resp.json()
            if 'data' in result and 'video' in result['data']:
                video_url = result['data']['video']
                print(f"[+] 解析成功，视频地址：{video_url}")
                return video_url
            else:
                print("[-] 解析失败，返回数据中没有视频链接。")
                print("[-] 原始响应内容：", result)
                return None
        else:
            print(f"[-] 请求失败，状态码：{resp.status_code}")
            return None
    except Exception as e:
        print(f"[-] 请求异常：{e}")
        return None

# 下载视频函数
def download_video(video_url, output_path="downloaded_video.mp4"):
    try:
        print(f"[+] 开始下载视频到：{output_path}")
        with requests.get(video_url, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[+] 视频下载完成：{output_path}")
    except Exception as e:
        print(f"[-] 下载失败：{e}")

# 主函数
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[-] 用法: python video_parser.py <视频链接>")
        sys.exit(1)

    input_url = sys.argv[1]
    print(f"[+] 正在解析视频链接：{input_url}")

    video_url = parse_video(input_url)
    if video_url:
        print(f"[+] 解析成功：{video_url}")
        choice = input("是否下载该视频？(y/n): ").strip().lower()
        if choice == 'y':
            download_path = input("请输入保存路径（默认为当前目录）[downloaded_video.mp4]: ").strip()
            if not download_path:
                download_path = "downloaded_video.mp4"
            download_video(video_url, download_path)
    else:
        print("[-] 解析失败，请检查链接或重试")