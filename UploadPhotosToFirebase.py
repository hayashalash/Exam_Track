import os
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
firebase_credentials = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"
})

# Importing student images
image_folder = '../Images'
image_file_list = os.listdir(image_folder)


for image_file in image_file_list:
    file_name = f'{image_folder}/{image_file}'
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
