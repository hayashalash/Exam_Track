import pandas as pd
from datetime import datetime
import io
from enum import Enum

# Constants

STUDENT_NOT_FOUND = -1
STUDENT_CONFIRMED = -2
STUDENT_ALREADY_CONFIRMED = -3
STUDENT_ALREADY_ON_BREAK = -4

FUNC_SUCCESS = 0


class ManualConfirmReason(Enum):
    FACEREC = 'Face not recognized'
    PIC = "No picture in system"
    TIME = "Time Circumstances"
    OTHER = "Other"


class BreakReason(Enum):
    RESTROOM = 'Restroom'
    MEDICAL = "Medical"
    OTHER = "Other"


class StudentManager:
    def __init__(self):
        # Attendance and Confirmation

        self.students_attendance = {}  # tracks current state of exam attendance
        self.students_manual_confirm = {}  # students manually confirmed - will contain the reason
        self.students_auto_confirm = {}  # students auto confirmed

        self.manual_confirm_hist = {attr.value: 0 for attr in ManualConfirmReason}

        # Waiver

        self.students_waiver = []

        #

        self.students_submitted = []

        # Notes

        self.students_notes = {}
        self.notes_count = 0

        # Breaks

        self.students_breaks = {}  # contains: [number of breaks, list of time(seconds) and list of reasons for each break]
        self.current_break = {}  # contains : [timestamp of current break]

        self.breaks_reasons_hist = {attr.value: 0 for attr in BreakReason}

        # Dataframe
        self.dtype_dict = {
            "id": str,  # Specify 'id' column as string to preserve leading zeros
            "first_name": str,
            "last_name": str,
            "extra_time": str,
            "tuition": str,
            "major": str
        }

        self.table_df = pd.DataFrame(columns=list(self.dtype_dict.keys()))

        self.result_table_df = None

        # print(table_df.loc[table_df['ID']=='002', 'First Name'].values[0])

        '''def get_csv():
            table_df.to_csv('output.csv', index=False)'''

    # initiate attendance
    def students_initiate_attendance(self):
        list_id = self.table_df['id'].tolist()
        for i in list_id:
            self.students_attendance[i] = False

    # initiate result table
    def create_result_table(self):
        self.result_table_df = self.table_df.copy()
        self.result_table_df.drop(columns=['major'], inplace=True)
        self.result_table_df.drop(columns=['tuition'], inplace=True)
        self.result_table_df.drop(columns=['extra_time'], inplace=True)

        self.result_table_df['breaks'] = self.result_table_df['id'].map(lambda x: self.students_breaks.get(x, [0])[0])

        self.result_table_df['notes'] = self.result_table_df['id'].map(self.students_notes)
        self.result_table_df['notes'].fillna(0, inplace=True)
        self.result_table_df['notes'] = self.result_table_df['notes'].astype(int)

        def map_attendance(row):
            student_id = row['id']
            if student_id in self.students_waiver:
                return "Waiver"
            elif self.student_check_attendance(student_id):
                return "Attended"
            else:
                return "Absent"
        self.result_table_df['attendance'] = self.result_table_df.apply(map_attendance, axis=1)

        def map_break_time(row):
            if row['breaks'] > 0:
                total_time = divmod(self.student_get_break_time(row['id']), 60)
                return str(int(total_time[0])) + ' minutes ' + str(int(total_time[1])) + ' seconds'
            else:
                return 'None'
        self.result_table_df['break_time'] = self.result_table_df.apply(map_break_time, axis=1)

        def map_confirm_method(row):
            student_id = row['id']
            if row['attendance'] != 'Absent':
                if student_id in self.students_auto_confirm:
                    return 'Auto'
                else:
                    return 'Manual'
            else:
                return 'None'
        self.result_table_df['confirm_method'] = self.result_table_df.apply(map_confirm_method, axis=1)

    # CHECKING CSV FILE STRUCTURE
    def check_csv_struct(self):
        # Get the columns from the DataFrame
        df_columns = self.table_df.columns
        # Get the keys from the dtype dictionary
        dtype_keys = self.dtype_dict.keys()
        # Check if the columns match the keys in the dtype dictionary
        if set(df_columns) == set(dtype_keys):
            return True
        else:
            return False

    # READING CSV FILE

    def read_students_blob(self, csv_data):
        try:
            self.table_df = pd.read_csv(io.BytesIO(csv_data), dtype=self.dtype_dict)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
        return True

    def read_students_csv(self, filepath):
        try:
            self.table_df = pd.read_csv(filepath, dtype=self.dtype_dict)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
        return True

    # DATAFRAME / DICT GET

    def get_student_df_ref(self):
        return self.table_df

    def get_result_table_df_ref(self):
        return self.result_table_df

    def student_table_values(self):
        return self.table_df.values.tolist()

    def result_table_values(self):
        return self.result_table_df.values.tolist()

    def student_table_columns(self):
        return self.table_df.columns.tolist()

    def result_table_columns(self):
        return self.result_table_df.columns.tolist()

    def student_table_ids(self):
        return self.table_df['id'].tolist()

    def result_table_ids(self):
        return self.result_table_df['id'].tolist()

    def get_students_count(self):
        return len(self.students_attendance)

    def get_students_currently_attending(self):
        count = 0
        for value in self.students_attendance.values():
            if value == True:
                count += 1
        return count

    def get_manual_confirm_count(self):
        return len(self.students_manual_confirm)

    def get_manual_confirm_hist(self):
        return self.manual_confirm_hist

    def get_auto_confirm_count(self):
        return len(self.students_auto_confirm)

    def get_students_attendance_count(self):  # Current students plus the students that used waiver
        return len(self.students_manual_confirm) + len(self.students_auto_confirm)

    def get_waiver_count(self):
        return len(self.students_waiver)

    def get_breaks_count(self):
        return len(self.students_breaks)

    def student_get_break_time(self,student_id):
        if student_id not in self.students_breaks.keys():
            return 0
        # Calculate sum of seconds
        return sum(self.students_breaks[student_id][1])

    def get_avg_break_time(self):  # Returns average time in seconds (rounded down)
        total_seconds = 0
        for student_id in self.students_breaks.keys():
            total_seconds += self.student_get_break_time(student_id)
        if len(self.students_breaks) != 0:
            return int(total_seconds/len(self.students_breaks))
        return 0

    def get_notes_hist(self):
        return self.students_notes

    def get_breaks_reasons_hist(self):
        return self.breaks_reasons_hist

    def get_breaks_time_hist(self):
        breaks_time_hist = {}
        for student_id in self.students_breaks.keys():
            breaks_time_hist[student_id] = self.student_get_break_time(student_id)
        return breaks_time_hist

    # Student GET Attributes Functions
    def student_get_name(self, student_id):
        temp_first = "No"
        temp_last = "Name"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'first_name'].values[0]
            temp_last = self.table_df.loc[self.table_df['id'] == student_id, 'last_name'].values[0]
        return temp_first + ' ' + temp_last

    def student_get_extra_time(self, student_id):
        temp_first = "No"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'extra_time'].values[0]
        return temp_first

    def student_get_tuition(self, student_id):
        temp_first = "No"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'tuition'].values[0]
        return temp_first

    def student_get_major(self, student_id):
        temp_first = "No Major"
        if student_id in self.table_df['id'].values:
            temp_first = self.table_df.loc[self.table_df['id'] == student_id, 'major'].values[0]
        return temp_first

    # Attendance Functions: Confirm or Check
    def student_confirm_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            if self.students_attendance[student_id]:
                return STUDENT_ALREADY_CONFIRMED
            else:
                self.students_attendance[student_id] = True
                return STUDENT_CONFIRMED
        else:
            return STUDENT_NOT_FOUND

    def student_auto_confirm_attendance(self, student_id):
        res = self.student_confirm_attendance(student_id)
        if res != STUDENT_CONFIRMED:
            return res
        else:
            self.students_auto_confirm[student_id] = True
            return res

    def student_manual_confirm_attendance(self, student_id, reason):
        res = self.student_confirm_attendance(student_id)
        if res != STUDENT_CONFIRMED:
            return res
        else:
            self.students_manual_confirm[student_id] = reason
            # Check if reason matches any enum value
            if reason in [member.value for member in ManualConfirmReason]:
                self.manual_confirm_hist[reason] += 1
            else:
                self.manual_confirm_hist[ManualConfirmReason.OTHER.value] += 1
        return res

    def student_cancel_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            self.students_attendance[student_id] = False
            return FUNC_SUCCESS
        return STUDENT_NOT_FOUND

    def student_check_attendance(self, student_id):
        if student_id in self.students_attendance.keys():
            return self.students_attendance[student_id]
        return False

    def student_check_manual_attendance(self, student_id):
        if student_id in self.students_manual_confirm.keys():
            return True
        return False

    def student_check_manual_reason(self, student_id):
        if self.student_check_manual_attendance(student_id):
            return self.students_manual_confirm[student_id]
        else:
            return None

    # Break functions

    def student_in_break(self, student_id):  # Student currently on a break
        if not self.student_check_attendance(student_id):
            return False
        if student_id in self.current_break.keys():
            return True
        return False

    def student_had_break(self, student_id):  # Student had a break before
        if student_id in self.students_breaks.keys():
            return True
        return False

    def student_report_break(self, student_id, reason):
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        elif self.student_in_break(student_id):
            return STUDENT_ALREADY_ON_BREAK
        if student_id in self.students_breaks:
            self.students_breaks[student_id][0] += 1
            self.students_breaks[student_id][2].append(reason)
        else:
            self.students_breaks[student_id] = [1, [], []]
            self.students_breaks[student_id][2].append(reason)
        # Check if reason matches any enum value
        if reason in [member.value for member in BreakReason]:
            self.breaks_reasons_hist[reason] += 1
        else:
            self.breaks_reasons_hist[BreakReason.OTHER.value] += 1
        self.current_break[student_id] = datetime.now()
        return FUNC_SUCCESS

    def student_back_break(self, student_id):  # Student back from break
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        elif not self.student_in_break(student_id):
            return STUDENT_NOT_FOUND
        cur_time = datetime.now()
        dif = cur_time - self.current_break[student_id]
        self.students_breaks[student_id][1].append(int(dif.total_seconds()))
        total_time = divmod(dif.total_seconds(), 60)
        total_time_string = 'Total Break time: ' + str(int(total_time[0])) + ' minutes ' + str(int(total_time[1])) + ' seconds'
        del self.current_break[student_id]
        return total_time_string

    def student_total_break_time(self, student_id):
        if not self.student_had_break(student_id):
            return STUDENT_NOT_FOUND
        return sum(self.students_breaks[student_id][1])

    def student_total_breaks(self, student_id):
        if not self.student_had_break(student_id):
            return STUDENT_NOT_FOUND
        return self.students_breaks[student_id][0]

    # Notes functions

    def student_report_note(self, student_id):
        if student_id in self.students_notes:
            # If the student exists, increment notes value by 1
            self.students_notes[student_id] += 1
        else:
            # otherwise, initiate
            self.students_notes[student_id] = 1
        self.notes_count += 1

    def get_notes_count(self):
        return self.notes_count

    # Waiver functions

    def student_report_waiver(self, student_id):
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        self.student_cancel_attendance(student_id)
        self.students_waiver.append(student_id)
        return FUNC_SUCCESS

    def student_undo_waiver(self, student_id):
        if self.student_check_attendance(student_id):
            return STUDENT_ALREADY_CONFIRMED
        if self.student_confirm_attendance(student_id) != STUDENT_CONFIRMED or not self.student_check_waiver(student_id):
            return STUDENT_NOT_FOUND
        self.students_waiver.remove(student_id)
        return FUNC_SUCCESS

    def student_check_waiver(self, student_id):
        if student_id in self.students_waiver:
            return True
        return False

# SUBMIT functions

    def student_submit_exam(self, student_id):
        if not self.student_check_attendance(student_id):
            return STUDENT_NOT_FOUND
        self.student_cancel_attendance(student_id)
        self.students_submitted.append(student_id)
        return FUNC_SUCCESS

    def student_undo_submit(self, student_id):
        if self.student_check_attendance(student_id):
            return STUDENT_ALREADY_CONFIRMED
        if self.student_confirm_attendance(student_id) != STUDENT_CONFIRMED or not self.student_check_submit(student_id):
            return STUDENT_NOT_FOUND

        self.students_submitted.remove(student_id)
        return FUNC_SUCCESS

    def student_check_submit(self, student_id):
        if student_id in self.students_submitted:
            return True
        return False

    def reset_att(self):

        self.students_attendance = {}
        self.students_manual_confirm = {}
        self.students_auto_confirm = {}

        self.manual_confirm_hist = {attr.value: 0 for attr in ManualConfirmReason}
        self.students_waiver = []
        self.students_submitted = []
        self.students_notes = {}
        self.notes_count = 0
        self.students_breaks = {}  # contains: [number of breaks, list of time(seconds) and list of reasons for each break]
        self.current_break = {}  # contains : [timestamp of current break]

        self.breaks_reasons_hist = {attr.value: 0 for attr in BreakReason}
        self.dtype_dict = {
            "id": str,  # Specify 'id' column as string to preserve leading zeros
            "first_name": str,
            "last_name": str,
            "extra_time": str,
            "tuition": str,
            "major": str
        }
        self.table_df = pd.DataFrame(columns=list(self.dtype_dict.keys()))
        self.result_table_df = None


students = StudentManager()


