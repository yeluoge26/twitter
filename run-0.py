import sys
import os
import glob
import time
import shutil
import requests
from twitter_fetch import get_tweets

MAX_POST_PAGE = 999
UNBAN_DELAY = 30
OUTPUT_DIR = 'output'


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def is_exist_file(dir_name, suffix):
    is_file = False
    reg = os.path.join(dir_name, suffix)
    if len(glob.glob(reg)):
        is_file = True
    return is_file


def download_videos(username, tweet_id, save_dir):
    if is_exist_file(save_dir, '*.mp4'):
        return
    url = 'https://twitter.com/{}/status/{}'.format(username, tweet_id)
    outdir = '\"./{}/%(title)s.%(ext)s\"'.format(save_dir)
    cmd = './video-downloader {} -o {}'.format(url, outdir)
    os.system(cmd)
    time.sleep(UNBAN_DELAY)


def download_photos(urls, save_dir):
    if is_exist_file(save_dir, '*.jpg'):
        return
    print('to download {} to {}'.format(len(urls), save_dir))
    for i, url in enumerate(urls):
        try:
            print(url)
            response = requests.get(url, stream=True)
        except Exception as err:
            print(err)
            continue
        img_name = os.path.join(save_dir, '{}.jpg'.format(i))
        with open(img_name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        time.sleep(UNBAN_DELAY)


def download_text(text, save_dir):
    with open(os.path.join(save_dir, 'text.txt'), 'w') as fp:
        fp.write(text)


def get_all_posts(username):
    dir_user = os.path.join(OUTPUT_DIR, username)
    mkdir(dir_user)
    # for p in range(1, MAX_POST_PAGE):
    print('\n\n crawling {} '.format(username))

    p_post_list = []
    try:
        p_post = get_tweets(username, pages=MAX_POST_PAGE)
        p_post_list = [tweet for tweet in p_post]
    except Exception as err:
        print(err)
    if len(p_post_list) == 0:
        print('Found no posts, exit!')
        return

    # launch crawler
    for post in p_post_list:
        if not post['isRetweet']:
            dir_name = os.path.join(dir_user, post['tweetId'])
            mkdir(dir_name)

            text = post['text']
            download_text(text, dir_name)

            photos = post['entries']['photos']
            if len(photos):
                download_photos(photos, dir_name)

            videos = post['entries']['videos']
            tweet_id = post['tweetId']
            if len(videos):
                download_videos(username, tweet_id, dir_name)

        # time.sleep(UNBAN_DELAY)


def main():    
    assert len(sys.argv) >= 2, 'python3 run.py user.txt'
    
    user_txt = sys.argv[1]
    mkdir(OUTPUT_DIR)
    with open(user_txt, 'r') as fp:
        content = fp.readlines()
        content = [x.strip() for x in content]
        for username in content:
            print(username)
            get_all_posts(username)
    

if __name__ == '__main__':
    main()
