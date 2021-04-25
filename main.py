#!/usr/bin/env python3
import requests
import sys
import traceback
import os

from argparse import ArgumentParser
from ch1p import State


def main():
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('--log-file', type=str, help='A file to read from')
    parser.add_argument('--state-file', default=('%s/.log-checker.state' % os.getenv('HOME')))
    parser.add_argument('--token', help='Telegram bot token')
    parser.add_argument('--chat-id', type=int, help='Telegram chat id (with bot)')
    args = parser.parse_args()

    # read file
    jstate = State(file=args.state_file, default=dict(seek=0, size=0))
    state = jstate.read()

    fsize = os.path.getsize(args.log_file)

    if fsize < state['size']:
        state['seek'] = 0

    with open(args.log_file, 'r') as f:
        if state['seek']:
            # jump to the latest readed position
            f.seek(state['seek'])

        # read till the end of the file
        content = f.read()

        # save new position
        state['seek'] = f.tell()
        state['size'] = fsize
        jstate.write(state)

        # if got something, send it to telegram
        if content != '':
            print('sending: %s' % content)
            r = requests.post('https://api.telegram.org/bot%s/sendMessage' % args.token, data={
                'chat_id': args.chat_id,
                'text': content
            })
            print(r.status_code)
            print(r.text)


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
        sys.exit(1)