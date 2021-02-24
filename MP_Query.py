import logging
import os
import platform
import sys
import time
import urllib3
import requests
from multiprocessing import Pool

# 关闭验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 定义请求头
headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/88.0.4324.104 Safari/537.36'
}

# 执行环境判断 建议统一使用secrets以免KEY泄露
if platform.system() == 'Linux':
    SCKEY = os.environ["SCKEY"]
    UID_UNAME = os.environ.get("UID_UNAME", None)
else:
    SCKEY = 'SCT****'
    # ‘13位uid 用户名’ 中间用空格相隔
    UID_UNAME = {
        '************* 用户1',
        '************* 用户2'
    }

# api
QUERY_API_ROOT = 'http://help.tencentbot.top'
PUSH_API_ROOT = 'https://sctapi.ftqq.com'

# 默认间隔
LONG_INTERVAL = 180
SHORT_INTERVAL = 10

# 设置日志格式
logger_raw = logging.getLogger()
logger_raw.setLevel(logging.INFO)
formatter1 = logging.Formatter("[%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler(stream=sys.stdout)  # 输出到控制台
console_handler.setFormatter(formatter1)
logger_raw.addHandler(console_handler)


# 推送
def push_service(msg):
    requests.post(
        f'{PUSH_API_ROOT}/{SCKEY}.send', params=msg, headers=headers, verify=False)
    logging.info('send message')


#
def get_rank(uid, uname) -> dict:

    # 获取rid,有异常则返回false(大概率为dns解析失败导致的与服务器连接不成功)
    try:
        rid = requests.get(
            f'{QUERY_API_ROOT}/enqueue?target_viewer_id={uid}', headers=headers, verify=False)
    except:
        logging.warning(uname + '连接失败，重试')
        return {'status': 'false'}

    # 与服务器成功连接后，判断响应码
    rid_response = rid.status_code
    if rid_response != 200:
        logging.warning(uname + '未取得rid,重试')
        return {'status': 'false'}

    else:
        rid_char = rid.json()['reqeust_id']
        # 成功获得rid
        while True:
            # 获取rank信息，有异常则返回false
            try:
                query = requests.get(
                    f'{QUERY_API_ROOT}/query?request_id={rid_char}', headers=headers, verify=False)
            except:
                logging.warning(uname + '连接失败，重试')
                return {'status': 'false'}

            query_response = query.status_code
            if query_response != 200:
                logging.warning(uname + '未取得排名，重试')
                return {'status': 'false'}

            else:
                logging.info(query.json()['status'])
                status = query.json()['status']

                # 查询rank，成功获得返回json，进行对key'status'的判断(done,queue,notfound)
                if status == 'done':
                    return query.json()

                elif status == 'queue':
                    logging.info(uname + '排队中')
                    time.sleep(SHORT_INTERVAL)

                elif status == 'notfound':
                    logging.warning(uname + 'rid过期，重试')
                    return {'status': 'false'}


# 初始化jjc排名
origin_arena_ranks = 15001
origin_grand_arena_ranks = 15001


# 排名变化相关的逻辑处理
def on_arena_schedule(uid, uname):
    # 全局变量,保存排名信息
    global origin_arena_ranks
    global origin_grand_arena_ranks

    # 循环调用get_rank()直到正确获得排名信息
    while True:
        data = get_rank(uid, uname)
        time.sleep(2)
        if data['status'] != 'false':
            break
        else:
            logging.warning('retrying')
            time.sleep(SHORT_INTERVAL)

    # 即时查询到的最新排名信息
    new_arena_ranks = int(data['data']['user_info']['arena_rank'])
    new_grand_arena_ranks = int(data['data']['user_info']['grand_arena_rank'])

    # jjc排名
    if origin_arena_ranks >= new_arena_ranks:
        origin_arena_ranks = new_arena_ranks
        logging.info(f'{uname}jjc:' + str(origin_arena_ranks))

    else:
        temp_arena_ranks = origin_arena_ranks
        origin_arena_ranks = new_arena_ranks
        url_params = {
            'title': f'{uname}:竞技场排名变化',
            'desp': f'竞技场排名发生变化:{temp_arena_ranks}->{new_arena_ranks}'
        }
        logging.info(f'{uname}竞技场排名发生变化:{temp_arena_ranks}->{new_arena_ranks}')
        push_service(url_params)

    # pjjc排名
    if origin_grand_arena_ranks >= new_grand_arena_ranks:
        origin_grand_arena_ranks = new_grand_arena_ranks
        logging.info(f'{uname}pjjc:' + str(origin_grand_arena_ranks))

    else:
        temp_grand_arena_ranks = origin_grand_arena_ranks
        origin_grand_arena_ranks = new_grand_arena_ranks
        url_params = {
            'text': f'{uname}:公主竞技场排名变化',
            'desp': f'公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}'
        }
        logging.info(f'{uname}公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}')
        push_service(url_params)


def info_split(uid_str):
    return uid_str.split(' ', 1)


def worker(uid_uname):
    while True:
        uid = info_split(uid_uname)[0]
        uname = info_split(uid_uname)[1]
        logging.info(uname + '----' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        on_arena_schedule(uid, uname)
        time.sleep(LONG_INTERVAL)


def main():
    po = Pool(len(UID_UNAME))
    for i in UID_UNAME:
        po.apply_async(worker, (i,))

    logging.info("----start----")
    po.close()
    po.join()
    logging.info("-----end-----")


if __name__ == '__main__':
    main()
