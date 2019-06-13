import os, requests, json_file, fetch_xckd, random, argparse
from dotenv import load_dotenv
from pprint import pprint

def get_vk(method, payload):
    url = 'https://api.vk.com/method/{}?v=5.95'.format(method)
    response = requests.get(url, params=payload)

    return response.json().get('response')


def get_server_address_to_upload_photos(access_token, group_id):
    method = 'photos.getWallUploadServer'
    payload = {
        'group_id':group_id,
        'access_token':access_token,
    }

    response = get_vk(method, payload)
    return None if response is None else response['upload_url']


def upload_photo(upload_url, directory, filename, caption):
    hash = None
    server = None
    photo = None

    filepath = os.path.join(directory, filename)

    files = {
        'photo': open(filepath, 'rb'),
        'Content-Type': 'multipart/form-data.',
        'caption': caption
            }
    response = requests.post(upload_url, files=files)
    if response is not None:
        hash = response.json()['hash']
        server = response.json()['server']
        photo = response.json()['photo']


    return hash, server, photo


def save_photo(access_token, user_id, group_id, photo, hash, server, caption):
    method = 'photos.saveWallPhoto'
    payload = {
        'user_id':user_id,
        'group_id':group_id,
        'photo':photo,
        'hash':hash,
        'server':server,
        'caption':caption,
        'access_token':access_token,
    }

    response = get_vk(method, payload)
    return None if response is None else 'photo{}_{}'.format(str(response[0]['owner_id']), str(response[0]['id']))


def post_on_wall(access_token, message, group_id, attachments=''):
    method = 'wall.post'
    payload = {
        'owner_id':'-' + group_id,
        'from_group': '1',
        'message':message,
        'attachments':attachments,
        'access_token':access_token,
    }

    get_vk(method, payload)


def post_image(directory, json_filename, image_id):
    access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    user_id = os.getenv("VK_USER_ID")

    file_contents = json_file.load_file(directory, json_filename)
    filename = file_contents[image_id]['filename']
    caption = file_contents[image_id]['description']
    title = file_contents[image_id]['title']
    filepath = os.path.join(directory, filename)

    upload_url = get_server_address_to_upload_photos(access_token, group_id)
    if upload_url is None:
        return
    hash, server, photo = upload_photo(upload_url, directory, filename, caption)
    if hash is None or server is None or photo is None:
        return
    attachments = save_photo(access_token, user_id, group_id, photo, hash, server, caption)
    if attachments is None:
        return
    post_on_wall(access_token, title, group_id, attachments)

    os.remove(filepath)

    file_contents[image_id]["posted"] = True
    json_file.write_file(directory, json_filename, file_contents)


def get_random_image_id(directory, json_filename, max_image_id):
    file_contents = json_file.load_file(directory, json_filename)

    not_posted_images = [image_id for image_id in file_contents if not file_contents[image_id]['posted']]
    if len(not_posted_images) == 0 :
        image_id = fetch_xckd.get_random_image_id(directory, json_filename, max_image_id)
    else:
        image_id = random.choice(not_posted_images)
    return image_id


def post_xckd_comics(image_info=None):
    load_dotenv()
    directory = os.getenv("DIRECTORY")
    json_filename = os.getenv("JSON_FILENAME")

    max_image_id = fetch_xckd.get_max_image_id()

    if image_info is None:
        image_id = str(max_image_id)
    elif image_info.upper() == 'RANDOM':
        image_id = get_random_image_id(directory, json_filename, max_image_id)
    elif not image_info.isdigit():
        return
    elif int(image_info) > int(max_image_id):
        return
    else:
        image_id = image_info

    file_contents = json_file.load_file(directory, json_filename)
    if image_id not in file_contents:
        fetch_xckd.fetch_xckd_comics(directory, json_filename, image_id)
        file_contents = json_file.load_file(directory, json_filename)


    if not file_contents[image_id]['posted']:
        post_image(directory, json_filename, image_id)


def main():
    parser = argparse.ArgumentParser(
       description='''Публикуем комиксы xckd про Python ВКонтакте'''
    )
    parser.add_argument('--image_info',
            help='''Укажите какой комикс с сайта xkcd.com хотите опубликовать:
                            random - любой еще не опубликованный, 
                            номер комикса - будет опубликован этот комикс,  
                            если ничего не указывать - будет опубликован последний комикс''')
    args = parser.parse_args()
    image_info = args.image_info

    print(image_info)
    post_xckd_comics(image_info)


if __name__ == "__main__":
  main()
