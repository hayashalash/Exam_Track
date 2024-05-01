import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from PyQt5.QtWidgets import *
import os



exam_number = "1"
room_number = "102"


# Initialize Firebase

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"
})
bucket = storage.bucket()

# Initialize the video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
img_background = cv2.imread('Resources/background.png')


# Load UI mode images
folder_mode_path = 'Resources/Modes'
mode_images = [cv2.imread(os.path.join(folder_mode_path, path)) for path in os.listdir(folder_mode_path)]

# Load encode file
print("Loading encode file...")
with open('EncodeFile.p', 'rb') as encode_file:
    encode_list_with_ids = pickle.load(encode_file)
encode_list_known, student_ids = encode_list_with_ids
print("Encode file loaded.")

current_mode = 0
counter = 0
student_id = -1
student_image = []
checked_flag = 0
tuition_flag = 0

# Define a practical font for putText
font = cv2.FONT_HERSHEY_TRIPLEX

while True:
    success, img = cap.read()

    # Resize and convert to RGB
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    # Find and encode faces
    face_locations = face_recognition.face_locations(img_small)
    face_encodings = face_recognition.face_encodings(img_small, face_locations)

    # Update UI
    img_background[162:162 + 480, 55:55 + 640] = img
    img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]

    if face_locations:
        for encode_face, face_loc in zip(face_encodings, face_locations):
            y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            img_background = cvzone.cornerRect(img_background, bbox, rt=0,colorC=(60, 60, 220))  #colorC=(220, 60, 80)
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_distances = face_recognition.face_distance(encode_list_known, encode_face)
            match_index = np.argmin(face_distances)

            if matches[match_index]:
                y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                img_background = cvzone.cornerRect(img_background, bbox, rt=0)  #colorC=(220, 60, 80)
                student_id = student_ids[match_index]

                if counter == 0:
                    counter = 1
                    current_mode = 1

                if counter != 0:
                    if counter == 1:
                        student_info = db.reference(f'Exams/{exam_number}/{room_number}/{student_id}').get()
                        blob = bucket.get_blob(f'Images/{student_id}.png')
                        img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                        temp = cv2.imdecode(img_data, cv2.COLOR_BGR2RGB)
                        student_image = cv2.copyMakeBorder(temp, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[198, 29, 222])

                        ref = db.reference(f'Exams/{exam_number}/{room_number}/{student_id}')

                        if student_info['tuition'] ==1:
                            tuition_flag = 1
                        else:
                            if student_info['checked'] != 1:
                                student_info['checked'] = 1
                                checked_flag = 1
                            ref.child('checked').set(student_info['checked'])

                    if current_mode != 3 and current_mode != 4:
                        if student_info['additional_time'] == 1:
                            additional_time = "Eligible"
                            time_color = (100, 240, 65)
                        else:
                            additional_time = "Ineligible"
                            time_color = (20, 20, 200)
                        if counter <= 10:
                            cv2.putText(img_background, str(student_info['number']), (861, 125),
                                        font, 1, (255, 255, 255), 1)
                            cv2.putText(img_background, str(student_info['major']), (1006, 550),
                                        font, 0.3, (255, 255, 255), 1)
                            cv2.putText(img_background, str(student_id), (1006, 493),
                                        font, 0.5, (255, 255, 255), 1)
                            cv2.putText(img_background, additional_time, (910, 625),
                                        font, 0.6, time_color, 1)
                            #cv2.putText(img_background, 'No', (1025, 625),
                            #            font, 0.6, (100, 100, 100), 1)
                            cv2.putText(img_background, str(student_info['starting_year']), (1125, 625),
                                        font, 0.6, (255, 255, 255), 1)
                            (w, h), _ = cv2.getTextSize(student_info['name'], font, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(img_background, str(student_info['name']), (808 + offset, 445),
                                        font, 1, (255, 255, 255), 1)
                        else:
                            counter = 0
                        img_background[175:175 + 226, 909:909 + 226] = student_image

                        """if student_info['checked'] == 1:
                            if checked_flag == 1:
                                if 10 < counter < 30:
                                    current_mode = 2
                                    img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]
                                elif counter > 30:
                                    current_mode = 3
                                    counter = 0
                                    img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]
                            else:
                                if counter > 10:
                                    current_mode = 3
                                    counter = 0
                                    img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]
                        else:
                            if counter > 10:
                                current_mode = 4
                                counter = 0
                                img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]
                        """

                    counter += 1

                    if counter >= 35:
                        counter = 0
                        checked_flag = 0
                        tuition_flag = 0
                        current_mode = 0
                        student_info = []
                        student_image = []
                        img_background[44:44 + 633, 808:808 + 414] = mode_images[current_mode]
    else:
        current_mode = 0
        counter = 0
        checked_flag = 0
        tuition_flag = 0

    cv2.namedWindow("Exam Attendance", cv2.WINDOW_NORMAL)
    cv2.imshow("Exam Attendance", img_background)
    cv2.resizeWindow("Exam Attendance",1280,680)
    cv2.waitKey(1)
