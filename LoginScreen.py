# importing required libraries
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import sys
import firebase_admin
from firebase_admin import credentials, db

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtGui import QPixmap

# Main window class
class MainWindow(QMainWindow):
	# constructor

	def __init__(self):
		super().__init__()

		self.room = -1
		self.exam = -1
		self.cam = -1


		# Initialize Firebase
		firebase_credentials = credentials.Certificate("serviceAccountKey.json")
		firebase_admin.initialize_app(firebase_credentials, {
			'databaseURL' : "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/"
		})

		# setting geometry
		self.setGeometry(100, 100,
						800, 500)

		# setting style sheet
		self.setStyleSheet("background-image: url(Resources/login_background.png)")

		# getting available cameras
		self.available_cameras = QCameraInfo.availableCameras()

		# if no camera found
		if not self.available_cameras:
			# exit the code
			sys.exit()


		# creating a QCameraViewfinder object
		self.viewfinder = QCameraViewfinder(self)

		# showing viewfinder
		self.viewfinder.show()

		# adjusting viewfinder
		self.viewfinder.resize(400,400)
		self.viewfinder.move(20,50)


		#labels and textbox
		self.label1 = QLabel("Room no.",self)
		self.label1.setStyleSheet("color: white;")
		self.label1.move(500,100)
		self.label2 = QLabel("Exam no.",self)
		self.label2.setStyleSheet("color: white;")
		self.label2.move(500,200)

		self.textbox_room = QLineEdit(self)
		self.textbox_room.move(500,150)
		self.textbox_room.setStyleSheet("color: white;")
		self.textbox_exam = QLineEdit(self)
		self.textbox_exam.move(500,250)
		self.textbox_exam.setStyleSheet("color: white;")


		self.button = QPushButton('Confirm', self)
		self.button.move(500,350)
		self.button.setStyleSheet("color: white;")

		self.button.clicked.connect(self.boo)

		#self.logo = QLabel(self)
		#self.pixmap = QPixmap('Resources/haifa-logo.png')
		#self.logo.setPixmap(self.pixmap)
		#self.logo.resize(self.pixmap.width(), self.pixmap.height())
		#self.logo.move(35,420)


		# Set the default camera.
		self.select_camera(0)

		# creating a combo box for selecting camera
		self.camera_selector = QComboBox(self)
		# adding tool tip to it
		self.camera_selector.setToolTip("Select Camera")
		self.camera_selector.setToolTipDuration(2500)

		# adding items to the combo box
		self.camera_selector.addItems([camera.description()
								for camera in self.available_cameras])

		# calling the select camera method
		self.camera_selector.currentIndexChanged.connect(self.select_camera)
		self.camera_selector.move(20,55)
		self.camera_selector.setStyleSheet("background : rgb(130, 145, 230);")
		self.camera_selector.resize(150,30)

		# setting window title
		self.setWindowTitle("Exam Attendance Login")

		# showing the main window
		self.show()

	# method to select camera
	def select_camera(self, i):

		# getting the selected camera
		self.camera = QCamera(self.available_cameras[i])

		# setting view finder to the camera
		self.camera.setViewfinder(self.viewfinder)

		self.cam = i
		# setting capture mode to the camera
		self.camera.setCaptureMode(QCamera.CaptureStillImage)

		# if any error occur show the alert
		self.camera.error.connect(lambda: self.alert(self.camera.errorString()))

		# start the camera
		self.camera.start()

		# creating a QCameraImageCapture object
		self.capture = QCameraImageCapture(self.camera)

		# showing alert if error occur
		self.capture.error.connect(lambda error_msg, error,
								msg: self.alert(msg))

		# when image captured showing message
		self.capture.imageCaptured.connect(lambda d,
										i: self.status.showMessage("Image captured : "
																	+ str(self.save_seq)))

		# getting current camera name
		self.current_camera_name = self.available_cameras[i].description()

		# initial save sequence
		self.save_seq = 0

	# method for alerts
	def alert(self, msg):

		# error message
		error = QErrorMessage(self)

		# setting text to the error message
		error.showMessage(msg)

	def boo(self, event):
		exam_number = self.textbox_exam.text()
		room_number = self.textbox_room.text()

		temp_res = db.reference(f'Exams/{exam_number}/{room_number}').get()
		if temp_res == None:
			self.show_info_messagebox()
		else:
			self.room = room_number
			self.exam = exam_number
			firebase_admin.delete_app(firebase_admin.get_app())
			self.setGeometry(100, 100,
						1024, 768)
			self.close()

	def show_info_messagebox(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)

		# setting message for Message Box
		msg.setText("Incorrect Information!")

		# setting Message box window title
		msg.setWindowTitle("Warning")

		# declaring buttons on Message Box
		msg.setStandardButtons(QMessageBox.Ok)

		# start the app
		retval = msg.exec_()

	def paintEvent(self, event):
			painter = QPainter(self)
			painter.setPen(QColor(255, 255, 255))
			painter.drawRect(19, 99, 401, 301)


# Driver code
if __name__ == "__main__" :
	# create pyqt5 app
	App = QApplication(sys.argv)

	# create the instance of our Window
	window = MainWindow()

	# start the app
	sys.exit(App.exec())
