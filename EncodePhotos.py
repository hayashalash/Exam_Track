import cv2
import os
import face_recognition
import pickle

import FirebaseManager


class EncodePhotos:
    def __init__(self):
        # Importing student images
        self.image_folder = FirebaseManager.CACHE_FOLDER_LOCAL
        self.image_file_list = []
        self.image_list = []
        self.student_ids = []
        self.encode_list = []

    def create_img_list(self):
        self.image_file_list = os.listdir(self.image_folder)
        for image_file in self.image_file_list:
            self.image_list.append(cv2.imread(os.path.join(self.image_folder, image_file)))
            self.student_ids.append(os.path.splitext(image_file)[0])

    def find_encodings(self):
        for image in self.image_list:
            try:
                # Attempt to convert the image to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(image)
                if face_locations:  # Check if any faces are detected
                    encode = face_recognition.face_encodings(image)[0]
                    self.encode_list.append(encode)
                else:
                    print("No faces detected in the image.")
            except Exception as e:
                # Handle the exception (e.g., print an error message)
                print("Error processing image:", e)

    def encode_images(self):
        try:
            print("Encoding images....")
            self.find_encodings()
            encode_and_ids_list = [self.encode_list, self.student_ids]
            print("Encoding done.")

            with open("EncodeFile.p", 'wb') as encode_file:
                pickle.dump(encode_and_ids_list, encode_file)
            print("Encode file saved.")
            return True
        except Exception as e:
            print("An error occurred while encoding images:", e)
            return False


encode_photos = EncodePhotos()

