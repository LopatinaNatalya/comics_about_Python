import os, json


def load_file(directory, filename):
  try:
    file_path = os.path.join(directory, filename)
    with open(file_path, "r") as json_file:
        file_contents = json.load(json_file)
  except FileNotFoundError:
    file_contents = {}
  return file_contents


def write_file(directory, filename, file_contents):
  ensure_dir(directory)
  file_path = os.path.join(directory, filename)
  with open(file_path, "w") as json_file:
    json.dump(file_contents, json_file)


def ensure_dir(directory):
  os.makedirs(directory, mode=0o777, exist_ok = True)


def get_items_count(directory, json_filename):
  file_contents = load_file(directory, json_filename)
  return len(file_contents)


def exist_key(directory, json_filename, image_id):
  file_contents = load_file(directory, json_filename)
  return image_id in file_contents
