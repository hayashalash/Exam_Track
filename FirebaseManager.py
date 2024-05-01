import firebase_admin
from firebase_admin import credentials, db, storage
from enum import Enum

import os
import shutil

from StudentData import *

# Constants
CACHE_FOLDER_DOWNLOAD = '\\cachedPictures'
IMG_NOT_FOUND = "Resources/no_pic.png"
CACHE_FOLDER_LOCAL = 'cachedPictures'

FIREBASE_IMAGES_PATH = 'Images'
FIREBASE_EXAMS_PATH = 'Exams'
FIREBASE_NOTES_PATH = 'Notes'
FIREBASE_EXAM_STATUS_PATH = 'ExamStatus'
FIREBASE_REPORT_HISTORY_PATH = "ExamHistory"


class AppState(Enum):
    IDLE = "Idle"
    DOWNLOADING = "Downloading"
    ENCODING = "Encoding"
    FAILED = "Failed"
    DONE = "Done"
    LOADED = "Loaded"


def delete_cache_dir():
    current_directory = os.getcwd()
    cache_dir = current_directory + CACHE_FOLDER_DOWNLOAD
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)


def get_image_path(student_id):
    current_directory = os.getcwd()
    cache_dir = current_directory + CACHE_FOLDER_DOWNLOAD
    file_path = os.path.join(cache_dir, f'{student_id}.png')
    if os.path.exists(file_path):
        return file_path
    return IMG_NOT_FOUND


class FirebaseManager:

    def __init__(self):
        self.cred = credentials.Certificate("serviceAccountKey.json")
        try:
            self.exam_app = firebase_admin.initialize_app(self.cred, {
                'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
                'storageBucket': "examfacerecognition.appspot.com"}, name="ExamApp")
        except firebase_admin.exceptions.FirebaseError as e:
            # Handle Firebase initialization error
            print("Firebase initialization error:", e)

        self.bucket = storage.bucket(app=self.exam_app)
        self.state = AppState.IDLE
        self.images_state_dict = {}

    def reset_att(self):
        self.state = AppState.IDLE
        self.images_state_dict = {}

    def get_bucket(self):
        return self.bucket

    # cache images
    def cache_files_from_firebase(self, c_dir):
        current_directory = os.getcwd()
        cache_dir = current_directory + c_dir

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        students_id_list = students.student_table_ids()

        self.set_downloading()
        for s_id in students_id_list:
            blob = self.bucket.get_blob(f'{FIREBASE_IMAGES_PATH}/{s_id}.png')
            if blob is None:  # no picture retrieved from database
                continue
            if f'{s_id}.png' in self.images_state_dict.keys():
                if self.images_state_dict[f'{s_id}.png']:  # picture was downloaded already
                    continue
                else:
                    self.images_state_dict[f'{s_id}.png'] = True
            # Construct local file path
            local_file_path = os.path.join(cache_dir, f'{s_id}.png')
            # Download file from Firebase Storage to local cache
            try:
                blob.download_to_filename(local_file_path)
                print(local_file_path, "downloaded successfully.")
                self.images_state_dict[f'{s_id}.png'] = True
            except Exception as e:
                print(local_file_path, f"Download error: {str(e)}")

    def get_csv_file(self, exam_no, exam_term):
        blob = self.bucket.get_blob(f'{FIREBASE_EXAMS_PATH}/{exam_no}_{exam_term}.csv')
        if blob is None:
            return "Exam Error", "Exam was not found in database make sure input is correct or upload a file."
        csv_data = blob.download_as_string()
        if not students.read_students_blob(csv_data):
            return "Exam Error", "Failed to read file."
        if not students.check_csv_struct():
            return "Exam Error", "File structure does not match."
        return True

    # gets data of ongoing exams
    def get_exam_status_by_date(self, exam_date):

        ref = self.get_exam_status_reference()
        try:
            # Get the data for the specified date from Firebase
            data = ref.child(exam_date).get()
            if data:
                return data
            else:
                print(f"No data found for date: {exam_date}")
                return None
        except Exception as e:
            print(f"Error retrieving data for date {exam_date}: {e}")
            return None

    # Get student image path
    def get_all_image_list(self):
        b_list = self.bucket.list_blobs(prefix=FIREBASE_IMAGES_PATH)
        img_list = []
        for blob in b_list:
            img_list.append(os.path.basename(blob.name))
        return img_list

    def get_notes_reference(self):
        return db.reference(FIREBASE_NOTES_PATH, app=self.exam_app)

    def get_exam_status_reference(self):
        return db.reference(FIREBASE_EXAM_STATUS_PATH, app=self.exam_app)

    def get_report_history_reference(self):
        return db.reference(FIREBASE_REPORT_HISTORY_PATH, app=self.exam_app)

    def get_student_notes(self, student_id):
        return db.reference(f'{FIREBASE_NOTES_PATH}/{student_id}', app=self.exam_app)

    def set_idle(self):
        self.state = AppState.IDLE

    def set_downloading(self):
        self.state = AppState.DOWNLOADING

    def set_encoding(self):
        self.state = AppState.ENCODING

    def set_done(self):
        self.state = AppState.DONE

    def set_loaded(self):
        self.state = AppState.LOADED

    def set_failed(self):
        self.state = AppState.FAILED

    def get_state(self):
        return self.state

    # GETS PICTURE FROM FIREBASE
    '''def get_student_image(self, student_id):
        blob = self.bucket.get_blob(f'Images/{student_id}.png')
        if blob is None:  # no picture found
            return blob
        else:  # convert and display picture
            img_data = np.frombuffer(blob.download_as_string(), np.uint8)
            img_cvt = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
            return Image.fromarray(img_cvt)
    '''


firebase_manager = FirebaseManager()
