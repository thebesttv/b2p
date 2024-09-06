#!/usr/bin/env python

'''
读取 bbdown-raw/ 下的所有文件，生成 bbdown-raw.yaml，用于 yaml 的 items 域

样例：爆炸电台
    ./bbdown-raw.sh 'https://space.bilibili.com/53456/channel/collectiondetail?sid=149941'

样例：陈一枝你坐下
由于无法直接下载所有投稿，需要先生成 xxx的投稿视频.txt，再对里面的每一个视频进行下载
    BBDown 'https://space.bilibili.com/1937416537'
    while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ -n "$line" ]]; then
        ./bbdown-raw.sh "$line"
    fi
    done < 陈一枝你坐下的投稿视频.txt

下载完成后，运行此脚本，生成 bbdown-raw.yaml
'''

import os
import yaml

from main import logging
logger = logging.getLogger('bbdown-raw')

from main import get_sha256

if __name__ == '__main__':
    items = {}

    # find all files under bbdown-raw
    for root, dirs, files in os.walk('bbdown-raw'):
        for file in files:
            file_path = os.path.join(root, file)
            path_list = file_path.split(os.sep)

            bvid = path_list[1]
            page = int(path_list[2])
            title = os.path.splitext(path_list[3])[0]

            logger.info(f'Processing: {title}, bvid: {bvid}, page: {page}')

            if title in items:
                logger.warning(f'{title} already exists!')
                logger.warning(f'Old: {items[title]}')

            items[title] = {
                'bvid': bvid,
                'page': page,
                'sha256': get_sha256(file_path),
            }

    # write to file
    with open('bbdown-raw.yaml', 'w') as f:
        yaml.dump({'items': items}, f, encoding='utf-8', allow_unicode=True)
