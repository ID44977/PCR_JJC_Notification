import logging
import os
import platform
import sys
import time
import urllib3
import requests


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
    UID = os.environ["UID"]
else:
    SCKEY = 'default'
    UID = 'default'

# api
apiroot = 'http://help.tencentbot.top'
pushapiroot = 'https://sctapi.ftqq.com'

# 默认间隔
long_invl = 180
short_invl = 10

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
        f'{pushapiroot}/{SCKEY}.send', params=msg, headers=headers, verify=False)
    logging.info('send message')


#
def get_rank() -> dict:
    rid = requests.get(f'{apiroot}/enqueue?target_viewer_id={UID}', headers=headers, verify=False)
    logging.info('break point at get_rank56')
    rid_response = rid.status_code

    if rid_response != 200:
        logging.warning('未取得rid,重试')
        logging.warning('rid response code: ' + str(rid_response))
        # time.sleep(interval)
        return {'status': 'false'}
    else:
        logging.info('rid response code: ' + str(rid_response))
        rid_char = rid.json()['reqeust_id']
        while True:
            query = requests.get(f'{apiroot}/query?request_id={rid_char}', headers=headers, verify=False)
            logging.info('break point at get_rank70')
            query_response = query.status_code

            if query_response != 200:
                logging.warning('未取得排名，重试')
                logging.warning('rank response code: ' + str(query_response))
                # time.sleep(interval)
                return {'status': 'false'}
            else:
                logging.info('rank response code: ' + str(query_response))
                logging.info(query.json()['status'])
                status = query.json()['status']

                if status == 'done':
                    # return query.json()['data']['user_info']
                    return query.json()
                elif status == 'queue':
                    logging.info('排队中')
                    time.sleep(short_invl)
                elif status == 'notfound':
                    logging.warning('rid过期，重试')
                    # time.sleep(interval)
                    return {'status': 'false'}


# 初始化jjc排名
origin_arena_ranks = 15001
origin_grand_arena_ranks = 15001


# 排名变化相关的逻辑处理
def on_arena_schedule():
    global origin_arena_ranks
    global origin_grand_arena_ranks

    # 循环调用get_rank()直到正确获得排名信息
    while True:
        data = get_rank()
        time.sleep(short_invl)
        if data['status'] != 'false':
            # logging.info(data)
            break
        else:
            logging.warning('retrying')
            time.sleep(short_invl)

    new_arena_ranks = int(data['data']['user_info']['arena_rank'])
    new_grand_arena_ranks = int(data['data']['user_info']['grand_arena_rank'])

    if origin_arena_ranks >= new_arena_ranks:
        origin_arena_ranks = new_arena_ranks
        logging.info('jjc:' + str(origin_arena_ranks))
        # time.sleep(short_invl)
    else:
        temp_arena_ranks = origin_arena_ranks
        origin_arena_ranks = new_arena_ranks
        url_params = {
            'title': '竞技场排名变化',
            'desp': f'竞技场排名发生变化：{temp_arena_ranks}->{new_arena_ranks}'
        }
        logging.info(f'竞技场排名发生变化：{temp_arena_ranks}->{new_arena_ranks}')
        push_service(url_params)
        # time.sleep(short_invl)

    if origin_grand_arena_ranks >= new_grand_arena_ranks:
        origin_grand_arena_ranks = new_grand_arena_ranks
        logging.info('pjjc:' + str(origin_grand_arena_ranks))
        time.sleep(long_invl)
    else:
        temp_grand_arena_ranks = origin_grand_arena_ranks
        origin_grand_arena_ranks = new_grand_arena_ranks
        url_params = {
            'text': '公主竞技场排名变化',
            'desp': f'公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}'
        }
        logging.info(f'公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}')
        push_service(url_params)
        # time.sleep(long_invl)


def main():
    while True:
        on_arena_schedule()
        time.sleep(long_invl)


if __name__ == '__main__':
    main()
