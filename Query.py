import time
import os
import requests
import logging
import sys

SCKEY = os.environ["SCKEY"]
UID = os.environ["UID"]

apiroot = 'http://help.tencentbot.top'

interval = 60

logger_raw = logging.getLogger()
logger_raw.setLevel(logging.INFO)
formatter1 = logging.Formatter("[%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler(stream=sys.stdout)  # 输出到控制台
console_handler.setFormatter(formatter1)
logger_raw.addHandler(console_handler)


def push_service(msg):
    requests.get(
        f'https://sc.ftqq.com/{SCKEY}.send', params=msg, timeout=5)


def get_rank() -> dict:
    rid = requests.get(f'{apiroot}/enqueue?target_viewer_id={UID}', timeout=5)
    rid_char = rid.json()['reqeust_id']

    if rid is None:
        logging.exception('未取得rid,重试')
        get_rank()

    while True:
        query = requests.get(f'https://help.tencentbot.top/query?request_id={rid_char}', timeout=5)
        logging.info(query.json()['status'])
        status = query.json()['status']

        if status == 'done':
            return query.json()['data']['user_info']
        elif status == 'queue':
            logging.info('排队中')
            time.sleep(1)
        else:
            logging.exception('not found or else,重试')
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
        grand_arena_ranks = new_grand_arena_ranks
        logging.info('pjjc:' + str(grand_arena_ranks))
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
