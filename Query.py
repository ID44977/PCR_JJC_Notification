import time
import os
import requests
import logging
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

SCKEY = os.environ["SCKEY"]
UID = os.environ["UID"]

apiroot = 'https://help.tencentbot.top'

interval = 30

logger_raw = logging.getLogger()
logger_raw.setLevel(logging.INFO)
formatter1 = logging.Formatter("[%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler(stream=sys.stdout)  # 输出到控制台
console_handler.setFormatter(formatter1)
logger_raw.addHandler(console_handler)


def push_service(msg):
    requests.get(
        f'https://sc.ftqq.com/{SCKEY}.send', params=msg, timeout=5, verify=False)


def get_rank() -> dict:
    rid = requests.get(f'{apiroot}/enqueue?target_viewer_id={UID}', timeout=5, verify=False)
    rid_char = rid.json()['reqeust_id']
    rid_response = rid.status_code

    if rid_response != 200:
        logging.warning('未取得rid,重试')
        get_rank()

    while True:
        query = requests.get(f'https://help.tencentbot.top/query?request_id={rid_char}', timeout=5, verify=False)
        logging.info(query.json()['status'])
        status = query.json()['status']

        if status == 'done':
            return query.json()['data']['user_info']
        elif status == 'queue':
            logging.info('排队中')
            time.sleep(1)
        else:
            logging.warning('not found or else,重试')
            get_rank()


origin_arena_ranks = 15001
origin_grand_arena_ranks = 15001


def on_arena_schedule():
    global origin_arena_ranks
    global origin_grand_arena_ranks

    data = get_rank()

    new_arena_ranks = int(data['arena_rank'])
    new_grand_arena_ranks = int(data['grand_arena_rank'])

    if origin_arena_ranks >= new_arena_ranks:
        origin_arena_ranks = new_arena_ranks
        logging.info('jjc:' + str(origin_arena_ranks))
        time.sleep(1)
    else:
        temp_arena_ranks = origin_arena_ranks
        origin_arena_ranks = new_arena_ranks
        url_params = {
            'text': '竞技场排名变化',
            'desp': f'竞技场排名发生变化：{temp_arena_ranks}->{new_arena_ranks}'
        }
        logging.info(f'竞技场排名发生变化：{temp_arena_ranks}->{new_arena_ranks}')
        push_service(url_params)
        time.sleep(interval)

    if origin_grand_arena_ranks >= new_grand_arena_ranks:
        origin_grand_arena_ranks = new_grand_arena_ranks
        logging.info('pjjc:' + str(origin_grand_arena_ranks))
        time.sleep(interval)
    else:
        temp_grand_arena_ranks = origin_grand_arena_ranks
        origin_grand_arena_ranks = new_grand_arena_ranks
        url_params = {
            'text': '公主竞技场排名变化',
            'desp': f'公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}'
        }
        logging.info(f'公主竞技场排名发生变化：{temp_grand_arena_ranks}->{new_grand_arena_ranks}')
        push_service(url_params)
        time.sleep(interval)


while True:
    on_arena_schedule()
    time.sleep(interval)
