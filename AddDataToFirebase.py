import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase
firebase_credentials = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL' : "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference('Exams')

data = {
    "1":{
        "102":{
            "777777":
                {
                    "name": "Cristiano Ronaldo",
                    "major": "Economics",
                    "starting_year": 2018,
                    "checked": 0,
                    "additional_time": 1,
                    "number": 4,
                    "last_attendance_time" : "2022-12-11 00:54:34",
                    "tuition": 0
                },
            "963852":
                {
                    "name": "Elon Musk",
                    "major": "Physics",
                    "starting_year": 2020,
                    "checked": 0,
                    "additional_time": 0,
                    "number": 41,
                    "last_attendance_time" : "2022-12-11 00:54:34",
                    "tuition": 1
                },
            "243731":
                {
                    "name": "Adnan Atili",
                    "major": "Information Systems",
                    "starting_year": 2019,
                    "checked": 0,
                    "additional_time": 1,
                    "number": 33,
                    "last_attendance_time" : "2022-12-11 00:54:34",
                    "tuition": 0
                },
            "112233":
                {
                    "name": "Haya Shalash",
                    "major": "Information Systems",
                    "starting_year": 2020,
                    "checked": 0,
                    "additional_time": 1,
                    "number": 23,
                    "last_attendance_time" : "2022-12-11 00:54:34",
                    "tuition": 0
                }
        }
    }

}

for key, value in data.items():
    ref.child(key).set(value)
