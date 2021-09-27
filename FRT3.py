import tempfile
import os
import cv2
from google.cloud import storage


NEW_FILE_PREFIX="thumbnail_"
client = storage.Client()


def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    name = event['name']
    bucket = event['bucket']

    _, _name = os.path.split(name)
    if _name.startswith(NEW_FILE_PREFIX):
        print(f"Blob {name} is already resized.")
        return

    file_name = download(bucket, name)
    resize(file_name)
    upload(bucket, name, file_name)

    os.remove(file_name)


def download(bucket, blob_name):
    blob = client.bucket(bucket).blob(blob_name)
    _, _ext = os.path.splitext(blob.name)
    _, temp_local_filename = tempfile.mkstemp(suffix=_ext)
    blob.download_to_filename(temp_local_filename)
    print(f"Blob {blob_name} downloaded to {temp_local_filename}.")
    return temp_local_filename


def upload(bucket, blob_name, file_name):
    _dir, _name = os.path.split(blob_name)
    new_file_name = os.path.join(_dir, NEW_FILE_PREFIX + _name)
    new_blob = client.bucket(bucket).blob(new_file_name)
    new_blob.upload_from_filename(file_name)
    print(f'New image uploaded to: gs://{bucket}/{new_file_name}')


def resize(file_name):
    img = cv2.imread(file_name)
    height = img.shape[0]
    width = img.shape[1]
    print(f"Old blob width {width}, height {height}")

    dst = cv2.resize(img, (int(width/2), int(height/2)))
    cv2.imwrite(file_name, dst) # requierd ext
    print(f"New blob width {dst.shape[0]}, height {dst.shape[1]}")
    return file_name