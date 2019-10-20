# -*- coding: utf-8 -*-
import requests
import hashlib
import random
import json
import argparse
import workflow
from workflow import Workflow3
import sys

URL = u'https://fanyi-api.baidu.com/api/trans/vip/translate'

def translate(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    with open("config.json") as f:
        config = json.load(f)
    appid = config['username'].decode('utf8')
    key = config['key'].decode('utf8')
    lang_list = config['lang']
    salt = str(random.randint(32768, 65536)).decode('utf8')
    query = query.decode('utf8')
    code = appid + query + salt + key
    responses = []
    for lang in lang_list:
        values = {
            'from': 'auto',
            'to': lang,
            'q': query,
            'salt': salt,
            'appid': appid,
            'sign': hashlib.md5(code.encode('utf8')).hexdigest()
        }
        response = requests.post(URL, data=values, headers=headers)
        responses.append(response.json())
    return responses

def main(wf):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', default='', type=str)
    args = parser.parse_args()

    if(len(args.query) == 0):
        wf.add_item(
            valid=True,
            title='Waiting Inputs',
            icon=workflow.ICON_INFO,
            arg=""
        )
    else:
        responses = translate(args.query)
        LOGGER.debug(responses)
        for response in responses:
            if 'error_code' in response:
                wf.add_item(
                    valid=True,
                    title='Error code {} Error msg {}'.format(response['error_code'], response['error_msg']),
                    arg="",
                    icon=workflow.ICON_WARNING
                )
            else:
                wf.add_item(
                    valid=True,
                    title=response['trans_result'][0]['dst'],
                    arg=response['trans_result'][0]['dst'],
                    subtitle=response['to'],
                    icon='icon.png'
                )
    wf.send_feedback()

if __name__ == "__main__":
    wf = Workflow3()
    LOGGER = wf.logger
    sys.exit(wf.run(main))