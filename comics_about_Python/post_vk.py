import os, requests, json_file, fetch_xckd, random, argparse
from dotenv import load_dotenv
from pprint import pprint

def get_groups_admin(access_token):
    url='https://api.vk.com/method/groups.get?user_id=166113106&filter=admin&access_token={}&v=5.95'.format(access_token)

    response = requests.get(url)
    if response.ok:
        pprint(response.json())

def get_server_address_to_upload_photos(group_id, access_token):
    url = 'https://api.vk.com/method/photos.getWallUploadServer?group_id={}&access_token={}&v=5.95'.format(group_id, access_token)

    response = requests.get(url)
    if response.ok:
        upload_url = response.json()['response']['upload_url']
    return upload_url

def upload_photo(upload_url, directory, filename, caption):
    filepath = '{}/{}'.format(directory, filename)

    files = {
        'photo': open(filepath, 'rb'),
        'Content-Type': 'multipart/form-data.',
        'caption': caption
            }
    response = requests.post(upload_url, files=files)

    return response.json()['hash'], response.json()['server'], response.json()['photo']


def save_photo(user_id, group_id, photo, hash, server, caption, access_token):
    url='https://api.vk.com/method/photos.saveWallPhoto?user_id={}&group_id={}&photo={}&hash={}&server={}&caption={}&access_token={}&v=5.95'.format(user_id, group_id, photo, hash, server, caption, access_token)
    response = requests.get(url)
    return 'photo'+str(response.json()['response'][0]['owner_id'])+'_'+str(response.json()['response'][0]['id'])


def post_photo(message, group_id, attachments, access_token):
    from_group = '1'
    owner_id = '-' + group_id

    url='https://api.vk.com/method/wall.post?owner_id={}&from_group={}&attachments={}&message={}&access_token={}&v=5.95'.format(owner_id, from_group, attachments, message, access_token)
    response = requests.get(url)
    if response.ok:
        pprint(response.json())


def post_image(directory, json_filename, image_id):
    access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    user_id = os.getenv("VK_USER_ID")

    file_contents = json_file.load_file(directory, json_filename)
    filename = file_contents[image_id]['filename']
    caption = file_contents[image_id]['description']
    title = file_contents[image_id]['title']
    filepath = '{}/{}'.format(directory, filename)

    upload_url = get_server_address_to_upload_photos(group_id, access_token)
    hash, server, photo = upload_photo(upload_url, directory, filename, caption)
    attachments = save_photo(user_id, group_id, photo, hash, server, caption, access_token)
    post_photo(title, group_id, attachments, access_token)

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
    elif int(image_info) > int(max_image_id):
        return False
    else:
        image_id = image_info

    file_contents = json_file.load_file(directory, json_filename)
    if image_id in file_contents:
        if not file_contents[image_id]['posted']:
            post_image(directory, json_filename, image_id)
        else:
            return False
    else:
        fetch_xckd.fetch_xckd_comics(directory, json_filename, image_id)
        post_image(directory, json_filename, image_id)
    return True


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
