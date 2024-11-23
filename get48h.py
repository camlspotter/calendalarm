#!/usr/bin/env python
from typing import Any
import argparse
import datetime
import os.path
import glob
import pprint
import json
import re
from icecream import ic
from typeguard import typechecked
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch near future events from Google calendar')
    # parser.add_argument('mode', default= 'list', type=str, help='list: list events of near future.  calendars: show the available calendars')

    subparsers = parser.add_subparsers(dest='mode')
    parser_calendars = subparsers.add_parser('calendars', help='list calendars')

    parser_calendars = subparsers.add_parser('dump', help='dump the events in near future')
    
    parser_calendars = subparsers.add_parser('list', help='list the events in near future')
    
    parser_add_token = subparsers.add_parser('add-token', help='add a new account token')
    parser_add_token.add_argument('id', type=str, help='id')

    args = parser.parse_args()
    
    conf = load_config()

    match args.mode:
        case "calendars":
            calendars(conf)

        case "dump":
            dump(conf)

        case "list":
            list_command(conf)

        case "add-token":
            add_token(conf, args.id)

        case _:
            raise ValueError('unknown mode: list or calendars')

scopes = ['https://www.googleapis.com/auth/calendar.readonly']

flow = InstalledAppFlow.from_client_secrets_file('_data/app-credentials.json', scopes)

config = dict[str,dict[str, str]]

def calendars(conf : config) -> None:
    pprint.pprint(get_all_calendars(conf))

def dump(conf : config) -> None:
    now = datetime.datetime.now()
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = tomorrow + datetime.timedelta(days=1)

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    # +48 hours
    upto = (datetime.datetime.utcnow() + datetime.timedelta(days=2)).isoformat() + "Z"

    all_events = []

    for credId, cals in conf.items():
        all_events.extend(get_events(credId, list(cals.keys()), now_iso, upto))

    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date')))

    print(json.dumps(all_events))
    
def list_command(conf : config) -> None:
    now = datetime.datetime.now()
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = tomorrow + datetime.timedelta(days=1)

    print(f'こんにちは、今日は{today.month}月{today.day}日。時刻は{now.hour}時{now.minute}分です。')

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    # +48 hours
    upto = (datetime.datetime.utcnow() + datetime.timedelta(days=2)).isoformat() + "Z"

    all_events = []

    for credId, cals in conf.items():
        all_events.extend(get_events(credId, list(cals.keys()), now_iso, upto))

    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date')))

    # print(all_events)

    for e in all_events:
        start = e['start']
        if ('dateTime' in start):
            print(f'''{speak_dateTime(now, start['dateTime'])}、{e.get('summary', '名称不明')}。 ''')
        else:
            print(f'''{speak_date(now, start['date'])}、{e.get('summary', '名称不明')}。 ''')

    print('以上です。') # 1sec pause

calendars_json_fn = '_data/calendars.json'

def add_token(conf : config, id : str) -> None:
    if id in conf:
        print(f'Account ID {id} is already in {calendars_json_fn}')
        assert False
    service = get_service(id)
    cs = get_calendars(service)
    pprint.pprint(cs)
    conf[id] = cs
    with open(calendars_json_fn, 'w', encoding='utf-8') as file:
        json.dump(conf, file, ensure_ascii=False, indent= 4)
    print(f'''Added all the {id}'s calendars to {calendars_json_fn}. Remove unnecessary ones.''')
    
def get_all_calendars(conf : config) -> config:
    dict = {}
    for id in conf.keys():
        service = get_service(id)
        cs = get_calendars(service)
        dict[id] = cs
    return dict

def get_calendars(service : Any) -> dict[str,str]:
    cs = {}
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        items = { i['id'] : i['summary'] for i in calendar_list['items'] }
        cs.update(items)
        # print(f"{calendar['summary']}:\t{calendar['id']}")
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return cs

def token_fn(id : str) -> str:
    return f'_data/token-{id}.json'

def get_id(fn : str) -> str:
    result = re.search(r'token-(.*)\.json$', fn)
    if result:
        return result.group(1)
    else:
        assert False

def get_ids() -> list[str]:
    return [get_id(fn) for fn in glob.glob('_data/token-*.json')]

def get_events(
    credId : str,
    calendarIds : list[str],
    timeMin : str,
    timeMax : str,
) -> list[Any]:
    all_events = []

    service = get_service(credId)

    for calendarId in calendarIds:
        events_result = service.events().list(calendarId=calendarId, # ='primary'
                                              maxResults=100,
                                              singleEvents=True,
                                              orderBy='startTime',
                                              timeMin=timeMin,
                                              timeMax=timeMax,
                                            ).execute()
        events = events_result.get('items', [])
        
        if not events:
            pass
        else:
            all_events.extend(events)              
    
    return all_events

def get_service(
    id : str,
) -> Any:
    creds = None

    fn = token_fn(id)

    # 保存されたトークンがあれば読み込む
    if os.path.exists(fn):
        creds = Credentials.from_authorized_user_file(fn, scopes)

    # 有効なクレデンシャルが無い場合、新しく OAuth 2.0 フローを開始する
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = flow.run_local_server(port=0)

        # トークンを保存
        with open(fn, 'w') as token:
            token.write(creds.to_json())

    # Calendar API client
    return build('calendar', 'v3', credentials=creds)

def load_config() -> config:
    if os.path.exists(calendars_json_fn):
        with open(calendars_json_fn, 'r', encoding='utf-8') as file:
            return check_config(ic(json.load(file)))
    else:
        return {}

@typechecked
def check_config(conf : config) -> config:
    return conf

def speaktime(
    tm : datetime.time,
) -> str:
    if tm.minute == 0:
        return f'{tm.hour}時'
    elif tm.minute == 30:
        return f'{tm.hour}時半'
    else:
        return f'{tm.hour}時{tm.minute}分'

def speak_dateTime(
    now : datetime.datetime,
    dateTime : str,
) -> str:
    today=now.date()
    tomorrow = (now + datetime.timedelta(days=1)).date()
    day_after_tomorrow = (now + datetime.timedelta(days=2)).date()

    dt = datetime.datetime.fromisoformat(dateTime)
    date = dt.date()
    if date < today:
        return ''  # long effective event
    elif date == today:
        return speaktime(dt.time())
    elif date == tomorrow:
        return f'''明日の{speaktime(dt.time())}'''
    elif date == day_after_tomorrow:
        return f'''明後日の{speaktime(dt.time())}'''
    else:
        return f'''{date.month}月{date.day}日{speaktime(dt.time())}'''

def speak_date(
    now : datetime.datetime,
    date_str : str,
) -> str:
    today=now.date()
    tomorrow = (now + datetime.timedelta(days=1)).date()
    day_after_tomorrow = (now + datetime.timedelta(days=2)).date()

    dt = datetime.datetime.fromisoformat(date_str)
    date = dt.date()
    if date < today:
        return ''  # long effective event
    elif date == today:
        return ''
    elif date == tomorrow:
        return '明日'
    elif date == day_after_tomorrow:
        return 'あさって'
    else:
        return f'{date.month}月{date.day}日'

if __name__ == '__main__':
    main()
