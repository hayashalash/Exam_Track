from datetime import date


WAIVER_TIME = 30
EXTRA_TIME_PERCENTAGE = 0.25


class ExamConfig:

    def __init__(self, number=None, duration=None, term=None, supervisors=[], camera_no=None):
        self.exam_number = number
        self.exam_duration = duration
        self.exam_term = term
        self.exam_supervisors = list(supervisors)
        self.exam_camera = camera_no

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        self.exam_date = d1

        self.added_time = 0
        self.waiver_available = False

    def get_exam_number(self):
        return self.exam_number

    def get_exam_duration(self):
        return self.exam_duration

    def get_exam_term(self):
        return self.exam_term

    def get_exam_supervisors(self):
        return self.exam_supervisors

    def get_exam_camera(self):
        return self.exam_camera

    def get_exam_date(self):
        return self.exam_date

    def get_exam_added_time(self):
        return self.added_time

    def is_waiver_available(self):
        return self.waiver_available

    def add_time(self, duration):
        self.added_time += duration

    def set_all(self, number, duration, term, supervisors, camera_no):
        self.exam_number = number
        self.exam_duration = duration
        self.exam_term = term
        self.exam_supervisors = list(supervisors)
        self.exam_camera = camera_no

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        self.exam_date = d1

        self.waiver_available = False
        if term.lower() != 'moeda':
            self.waiver_available = True


cur_exam = ExamConfig()
