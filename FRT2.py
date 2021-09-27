import os
import cv2
import numpy as np
from google.cloud import storage
from tempfile import NamedTemporaryFile
def reformat_image(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    client = storage.Client()
    source_bucket = client.get_bucket(file['bucket'])
    source_blob = source_bucket.get_blob(file['name'])
    image = np.asarray(bytearray(source_blob.download_as_string()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
    scale_percent = 50  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    with NamedTemporaryFile() as temp:
        # Extract name to the temp file
        temp_file = "".join([str(temp.name), file['name']])
        # Save image to temp file
        cv2.imwrite(temp_file, resized)
        # Uploading the temp image file to the bucket
        dest_filename = file['name']
        dest_bucket_name = os.environ.get('PROCESSED_BUCKET_NAME', 'Specified environment variable is not set.')
        dest_bucket = client.get_bucket(dest_bucket_name)
        dest_blob = dest_bucket.blob(dest_filename)
        dest_blob.upload_from_filename(temp_file)