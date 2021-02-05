import time
import os
import requests
import logging
import sys

SCKEY = os.environ["SCKEY"]
UID = os.environ["UID"]

apiroot = 'http://help.tencentbot.top'


interval = 60

arena_ranks = 15001
grand_arena_ranks = 15001

logger_raw = logging.getLogger()
logger_raw.setLevel(logging.INFO)
formatter1 = logging.Formatter("[%(levelname)s]: %(message)s")
console_handler = logging.StreamHandler(stream=sys.stdout) #输出到控制台
console_handler.setFormatter(formatter1)
logger_raw.addHandler(console_handler)

def push_service():
    requests.get(
        f'https://sc.ftqq.com/{SCKEY}.send', params=url_params, timeout=5)


while True:
    time.sleep(interval)
    logging.info('start!')
    
    rid = requests.get(f'{apiroot}/enqueue?target_viewer_id={UID}', timeout=5)
    rid_char = rid.json()['reqeust_id']

    if len(rid_char) != 0:
        query = requests.get(f'https://help.tencentbot.top/query?request_id={rid_char}', timeout=5)

        logging.info(query.json()['status'])
        status = query.json()['status']

        if status == 'done':

            temp_arena_ranks = int(query.json()['data']['user_info']['arena_rank'])
            temp_grand_arena_ranks = int(query.json()['data']['user_info']['grand_arena_rank'])

            if arena_ranks >= temp_arena_ranks:
                arena_ranks = temp_arena_ranks
                logging.info('jjc:' + str(arena_ranks))
                time.sleep(1)
            else:
                new_arena_ranks = temp_arena_ranks
                arena_ranks = temp_arena_ranks
                url_params = {
                    'text': '竞技场排名变化',
                    'desp': f'竞技场排名发生变化：{arena_ranks}->{new_arena_ranks}'
                }
                push_service()
                logging.info(f'竞技场排名发生变化：{arena_ranks}->{new_arena_ranks}')
                time.sleep(interval)

            if grand_arena_ranks >= temp_grand_arena_ranks:
                grand_arena_ranks = temp_grand_arena_ranks
                logging.info('pjjc:' + str(grand_arena_ranks))
                time.sleep(10)
            else:
                new_grand_arena_ranks = temp_grand_arena_ranks
                grand_arena_ranks = temp_grand_arena_ranks
                url_params = {
                    'text': '公主竞技场排名变化',
                    'desp': f'公主竞技场排名发生变化：{grand_arena_ranks}->{new_grand_arena_ranks}'
                }
                push_service()
                logging.info(f'公主竞技场排名发生变化：{grand_arena_ranks}->{new_grand_arena_ranks}')
                time.sleep(interval)

        elif status == 'queue':
            time.sleep(1)
        else:
            logging.error('not found or else')
            time.sleep(3)
    else:
        logging.error('rid err')
        time.sleep(3)

