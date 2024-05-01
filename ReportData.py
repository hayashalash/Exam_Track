import json
import pandas as pd
import io
from datetime import datetime,date


import ExamConfig
import StudentData

import FirebaseManager


class ReportData:
    def __init__(self):
        self.exam = None
        self.students = None

        self.students_df = None

        self.exam_number = None
        self.term = None
        self.date = None
        self.duration = None
        self.added_time = None
        self.waiver_available = None
        self.enlisted_count = None
        self.attendance_count = None
        self.auto_confirm_count = None
        self.manual_confirm_count = None
        self.manual_confirm_hist = None
        self.waiver_count = None
        self.notes_count = None
        self.breaks_count = None
        self.avg_break_time = None
        self.notes_hist = None
        self.breaks_reasons_hist = None
        self.breaks_time_hist = None

        self.firebase_manager = FirebaseManager.firebase_manager

    def create_new_report(self):

        self.exam = ExamConfig.cur_exam
        self.students = StudentData.students

        self.students_df = self.students.get_result_table_df_ref()

        # Exam Related Attributes
        self.exam_number = self.exam.get_exam_number()
        self.term = self.exam.get_exam_term()
        self.date = self.exam.get_exam_date()
        self.duration = self.exam.get_exam_duration()
        self.added_time = self.exam.get_exam_added_time()
        self.waiver_available = self.exam.is_waiver_available()

        # Students Related Attributes
        self.enlisted_count = self.students.get_students_count()
        self.attendance_count = self.students.get_students_attendance_count()
        self.auto_confirm_count = self.students.get_auto_confirm_count()
        self.manual_confirm_count = self.students.get_manual_confirm_count()
        self.manual_confirm_hist = self.students.get_manual_confirm_hist()
        self.waiver_count = self.students.get_waiver_count()
        self.notes_count = self.students.get_notes_count()
        self.breaks_count = self.students.get_breaks_count()
        self.avg_break_time = self.students.get_avg_break_time()
        self.notes_hist = self.students.get_notes_hist()
        self.breaks_reasons_hist = self.students.get_breaks_reasons_hist()
        self.breaks_time_hist = self.students.get_breaks_time_hist()

    # Getter methods
    def get_students_table(self):
        return self.students_df

    def get_exam_number(self):
        return self.exam_number

    def get_term(self):
        return self.term

    def get_date(self):
        return self.date

    def get_duration(self):
        return self.duration

    def get_added_time(self):
        return self.added_time

    def is_waiver_available(self):
        return self.waiver_available

    def get_enlisted_count(self):
        return self.enlisted_count

    def get_attendance_count(self):
        return self.attendance_count

    def get_auto_confirm_count(self):
        return self.auto_confirm_count

    def get_manual_confirm_count(self):
        return self.manual_confirm_count

    def get_manual_confirm_hist(self):
        return self.manual_confirm_hist

    def get_waiver_count(self):
        return self.waiver_count

    def get_notes_count(self):
        return self.notes_count

    def get_breaks_count(self):
        return self.breaks_count

    def get_avg_break_time(self):
        return self.avg_break_time

    def get_notes_hist(self):
        return self.notes_hist

    def get_breaks_reasons_hist(self):
        return self.breaks_reasons_hist

    def get_breaks_time_hist(self):
        return self.breaks_time_hist

    def save_report_firebase(self):
        if self.exam_number is None:
            return

        bucket = self.firebase_manager.get_bucket()

        # Convert the input date string to a datetime object
        date_object = datetime.strptime(self.date, "%d/%m/%Y")

        # Format the datetime object as "ddmmyy"
        formatted_date = date_object.strftime("%d%m%y")

        json_blob = bucket.blob(f"{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/Report_{self.exam_number}_{self.term}_"
                                f"{formatted_date}/report.json")

        try:
            # Save the DataFrame as a CSV file
            csv_data = self.students_df.to_csv(index=False)
            csv_blob = bucket.blob(f"{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/Report_{self.exam_number}_{self.term}_"
                                f"{formatted_date}/data.csv")
            csv_blob.upload_from_string(csv_data, content_type='text/csv')
        except Exception as e:
            print("Failed to upload CSV file to Firebase Storage:", e)
            return

        # Prepare the data to be saved
        data = {
            "exam_number": self.exam_number,
            "term": self.term,
            "date": self.date,
            "duration": self.duration,
            "added_time": self.added_time,
            "waiver_available": self.waiver_available,
            "enlisted_count": self.enlisted_count,
            "attendance_count": self.attendance_count,
            "auto_confirm_count": self.auto_confirm_count,
            "manual_confirm_count": self.manual_confirm_count,
            "manual_confirm_hist": self.manual_confirm_hist,
            "waiver_count": self.waiver_count,
            "notes_count": self.notes_count,
            "breaks_count": self.breaks_count,
            "avg_break_time": self.avg_break_time,
            "notes_hist": self.notes_hist,
            "breaks_reasons_hist": self.breaks_reasons_hist,
            "breaks_time_hist": self.breaks_time_hist
        }

        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            # Upload JSON data to Firebase Storage
            json_blob.upload_from_string(json_data)

            print("Saved report to Firebase Storage.")
        except ValueError:
            print("Failed to save report to Firebase Storage.")

    def load_report_from_firebase(self, folder_name):

        bucket = self.firebase_manager.get_bucket()

        try:
            json_blob = bucket.blob(f"{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/{folder_name}/report.json")
            # Download the JSON file
            json_data = json_blob.download_as_string()
            # Parse the JSON data into Python objects
            data = json.loads(json_data)

            # Load the CSV file into self.student_df
            csv_blob = bucket.blob(f"{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/{folder_name}/data.csv")
            csv_data = csv_blob.download_as_string()
            self.students_df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            self.students_df = self.students_df.fillna('None')

            # Assign the values to variables
            self.exam_number = data["exam_number"]
            self.term = data["term"]
            self.date = data["date"]
            self.duration = data["duration"]
            self.added_time = data["added_time"]
            self.waiver_available = data["waiver_available"]
            self.enlisted_count = data["enlisted_count"]
            self.attendance_count = data["attendance_count"]
            self.auto_confirm_count = data["auto_confirm_count"]
            self.manual_confirm_count = data["manual_confirm_count"]
            self.manual_confirm_hist = data["manual_confirm_hist"]
            self.waiver_count = data["waiver_count"]
            self.notes_count = data["notes_count"]
            self.breaks_count = data["breaks_count"]
            self.avg_break_time = data["avg_break_time"]
            self.notes_hist = data["notes_hist"]
            self.breaks_reasons_hist = data["breaks_reasons_hist"]
            self.breaks_time_hist = data["breaks_time_hist"]

            print("Loaded report from Firebase Storage.")
            return True

        except Exception as e:
            print("Failed to load report from Firebase Storage:", e)
            return False

    def update_exam_status(self, time_left, current_attendance, status):
        if self.exam_number is None:
            return
        ref = self.firebase_manager.get_exam_status_reference()
        data = {
            "term": self.term,
            "time_left": time_left,
            "current_attendance": current_attendance,
            "status": status,
            "duration": self.duration,
            "added_time": self.added_time,
            "enlisted_count": self.enlisted_count,
            "attendance_count": self.attendance_count,
            "auto_confirm_count": self.auto_confirm_count,
            "manual_confirm_count": self.manual_confirm_count,
            "waiver_count": self.waiver_count,
            "notes_count": self.notes_count,
            "breaks_count": self.breaks_count,
            "avg_break_time": self.avg_break_time,
        }
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y")
        json_data = {
            dt_string: {
                self.exam_number: data
            }
        }
        try:
            for key, value in json_data.items():
                ref.child(key).update(value)
            return True
        except ValueError:
            return False


cur_report = ReportData()
