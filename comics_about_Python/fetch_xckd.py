import os, random, requests, json_file
from dotenv import load_dotenv


def get_max_image_id():
    url = 'http://xkcd.com/info.0.json'
    response = requests.get(url)
    return response.json()['num'] if response.ok else None


def get_image(directory, img, json_filename, files_info):
    filename = os.path.basename(img)
    file_path = os.path.join(directory, filename)
    response = requests.get(img)
    if response.ok:
        with open(file_path, 'wb') as file:
            file.write(response.content)

        json_file.write_file(directory, json_filename, files_info)


def fetch_xckd_comics(directory, json_filename, image_id=None):
    if not image_id:
        url='http://xkcd.com/info.0.json'
    else:
        url='http://xkcd.com/{}/info.0.json'.format(image_id)

    response = requests.get(url)
    if not response.ok:
        return

    description = response.json()['alt']
    title = response.json()['safe_title']
    image_id = response.json()['num']
    filename = os.path.basename(response.json()['img'])
    img = response.json()['img']

    files_info = json_file.load_file(directory, json_filename)
    if image_id not in files_info:
        files_info[image_id] = {
                    "title": title,
                    "filename": filename,
                    "description": description,
                    "posted": False
             }

        get_image(directory, img, json_filename, files_info)


def get_random_image_id(directory, json_filename, max_image_id):
    file_contents = json_file.load_file(directory, json_filename)
    loaded_images = file_contents.keys()
    missing_images = []
    for image in range(1, max_image_id + 1):
        if str(image) in loaded_images:
            continue
        missing_images.append(str(image))

    image_id = random.choice(missing_images)
    return image_id


def fetch_xckd_random_comics(directory, json_filename):
    json_file.ensure_dir(directory)
    max_image_id = get_max_image_id()
    if max_image_id is None:
        return None

    image_id = get_random_image_id(directory, json_filename, max_image_id)
    if image_id is not None:
       fetch_xckd_comics(directory, json_filename, image_id)

    return image_id


def main():
    load_dotenv()

    directory = os.getenv("DIRECTORY")
    json_filename = os.getenv("JSON_FILENAME")

    fetch_xckd_random_comics(directory, json_filename)


if __name__ == "__main__":
  main()
