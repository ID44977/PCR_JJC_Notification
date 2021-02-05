import time
import os
import requests
import datetime

SCKEY = os.environ["SCKEY"]
UID = os.environ["UID"]

apiroot = 'http://help.tencentbot.top'


interval = 60

arena_ranks = 15001
grand_arena_ranks = 15001


def push_service():
    requests.get(
        f'https://sc.ftqq.com/{SCKEY}.send', params=url_params)


while True:
    rid = requests.get(f'{apiroot}/enqueue?target_viewer_id={UID}')
    print(rid.json())
    rid_char = rid.json()['reqeust_id']
    print(rid_char)
    query = requests.get(f'https://help.tencentbot.top/query?request_id={rid_char}')

    print(query.json()['status'])
    status = query.json()['status']

    if status == 'done':

        temp_arena_ranks = int(query.json()['data']['user_info']['arena_rank'])
        temp_grand_arena_ranks = int(query.json()['data']['user_info']['grand_arena_rank'])

        if arena_ranks >= temp_arena_ranks:
            arena_ranks = temp_arena_ranks
            print('jjc:'+str(arena_ranks))
            time.sleep(1)
        else:
            new_arena_ranks = temp_arena_ranks
            arena_ranks = temp_arena_ranks
            url_params = {
                'text': '竞技场排名变化',
                'desp': f'竞技场排名发生变化：{arena_ranks}->{new_arena_ranks}'
            }
            push_service()
            print(f'竞技场排名发生变化：{arena_ranks}->{new_arena_ranks}')
            print(datetime.datetime.now())
            time.sleep(interval)

        if grand_arena_ranks >= temp_grand_arena_ranks:
            grand_arena_ranks = temp_grand_arena_ranks
            print('pjjc:'+str(grand_arena_ranks))
            time.sleep(10)
        else:
            new_grand_arena_ranks = temp_grand_arena_ranks
            grand_arena_ranks = temp_grand_arena_ranks
            url_params = {
                'text': '公主竞技场排名变化',
                'desp': f'公主竞技场排名发生变化：{grand_arena_ranks}->{new_grand_arena_ranks}'
            }
            push_service()
            print(f'公主竞技场排名发生变化：{grand_arena_ranks}->{new_grand_arena_ranks}')
            print(datetime.datetime.now())
            time.sleep(interval)

    elif status == 'queue':
        time.sleep(3)
    else:
        print('not found or else')
        time.sleep(3)

