import yaml
import json
import os
import sys
import shutil
import subprocess
import logging
from tqdm import tqdm

DEBUG_ENABLED = True if os.getenv('ACTIONS_RUNNER_DEBUG') == 'true' else False

################################################################
# Logging
################################################################

def config_logger(log_file):
    LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger(None).addHandler(console)

config_logger('log')
logger = logging.getLogger('main')

################################################################
# Main
################################################################

def get_sha256(file_name) -> str:
    '''Compute the sha256 hash of a file.'''
    import hashlib
    with open(file_name, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def gen_dir2cast_ini(config) -> str:
    '''Generate content of dir2cast.ini from config.'''
    data = {
        'TITLE': config['title'],
        'ITUNES_AUTHOR': config['author'],
        'LINK': config['link'],
        'ITEM_COUNT': len(config['items']),
    }

    result = ''
    for key, value in data.items():
        # 使用 json.dumps() 来转义字符串
        # 使用 ensure_ascii=False 保证中文不会被转义
        value = json.dumps(value, ensure_ascii=False)
        result += f'{key} = {value}\n'

    return result

def copy_dir2cast(root, target):
    '''Copy root/{dir2cast.php,getID3/} to target'''
    for item in ['dir2cast.php', 'getID3']:
        src = os.path.join(root, item)
        dst = os.path.join(target, item)
        if os.path.exists(dst):
            logger.warning(f'{dst} already exists!')
        else:
            logger.info(f'Copying: {src} -> {dst}')
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)

def make_podcast(config_path, output_dir):

    def handle_item(title: str, value: dict):
        bvid = value['bvid']
        page = value.get('page', 1)
        sha256 = value.get('sha256', None)

        logger.info(f'Generating: {title}, bvid: {bvid}, page: {page}')

        cmd = [
            'BBDown',
            '--audio-only',
            '--file-pattern', title,
            '--select-page', str(page),
            bvid
        ]
        result = subprocess.run(cmd, cwd=output_dir,
                                # 如果 debug，就不捕获输出，直接输出到终端
                                capture_output=not DEBUG_ENABLED)
        if result.returncode != 0:
            logger.error("Return code is not 0!")
            logger.error(result.stdout.decode())
            logger.error(result.stderr.decode())

        file_name = os.path.join(output_dir, f'{title}.m4a')
        assert os.path.exists(file_name), f'{file_name} not found!'

        # check sha256
        new_sha256 = get_sha256(file_name)
        if sha256 is not None:
            if new_sha256 != sha256:
                logger.error(f'Sha256 check failed!')
                logger.error(f'  Expected: {sha256}')
                logger.error(f'  Got:      {new_sha256}')
                raise ValueError('Sha256 check failed!')
            else:
                logger.info('Sha256 check passed.')
        else:
            logger.warning(f'No sha256 provided, new sha256: {new_sha256}')
            value['sha256'] = new_sha256

    os.makedirs(output_dir, exist_ok=True)

    logger.info("Loading config...")
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if 'icon' in config:
        icon = config['icon']
        icon_path = os.path.join(output_dir, 'image.jpg')
        logger.info(f"Icon found: {icon}")
        logger.info(f"  Copying to {icon_path}")
        shutil.copyfile(icon, icon_path)

    ini_path = os.path.join(output_dir, 'dir2cast.ini')
    with open(ini_path, 'w') as f:
        f.write(gen_dir2cast_ini(config))
        logger.info(f"dir2cast.ini saved to: {ini_path}")

    items = config['items']
    logger.info(f"Generating podcast for {len(items)} items...")
    for title, value in tqdm(items.items()):
        handle_item(title, value)

    items_path = os.path.join(output_dir, 'items.yaml')
    with open(items_path, 'w') as f:
        yaml.dump({'items': items}, f, encoding='utf-8', allow_unicode=True)
    logger.info(f"Items with sha256 saved to: {items_path}")

    logger.info("Adding dir2cast to output...")
    copy_dir2cast('dir2cast', output_dir)

if __name__ == '__main__':
    config_path = sys.argv[1]

    # 获取 a/b/c/xxx.yaml 中的 xxx
    config_name = os.path.basename(config_path)
    config_name = os.path.splitext(config_name)[0]

    output_dir = os.path.join(os.getcwd(), 'output', config_name)

    make_podcast(config_path, output_dir)
