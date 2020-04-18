import requests
from dotenv import load_dotenv
import os
import random


def download_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def get_xkcd_num():
    api_url = 'https://xkcd.com/info.0.json'
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()['num']


def download_random_xkcd_image(filename):
    num = get_xkcd_num()
    image_id = random.randint(1, num)
    api_url = 'https://xkcd.com/{}/info.0.json'.format(image_id)
    response = requests.get(api_url)
    response.raise_for_status()
    image_link = response.json()['img']
    download_image(image_link, filename)
    return response.json()['alt']


def post_photo_to_vk_group(access_token, group_id, filename, comment):
    payload = {
        'access_token': access_token,
        'v': 5.103,
        'group_id': group_id
    }
    api_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(api_url, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']

    with open('pic.png', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

    os.remove('pic.png')

    photo = response.json()['photo']
    server = response.json()['server']
    vkhash = response.json()['hash']
    payload = {
        'access_token': access_token,
        'v': 5.103,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': vkhash
    }
    api_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(api_url, params=payload)
    response.raise_for_status()

    media_id = response.json()['response'][0]['id']
    owner_id = response.json()['response'][0]['owner_id']

    payload = {
        'access_token': access_token,
        'v': 5.103,
        'owner_id': -group_id,
        'from_group': 1,
        'attachments': 'photo{}_{}'.format(owner_id, media_id),
        'message': comment
    }
    api_url = 'https://api.vk.com/method/wall.post'
    response = requests.post(api_url, params=payload)
    response.raise_for_status()


if __name__ == '__main__':
    filename = 'pic.png'
    comment = download_random_xkcd_image(filename)

    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    group_id = 194377570

    post_photo_to_vk_group(access_token, group_id, filename, comment)