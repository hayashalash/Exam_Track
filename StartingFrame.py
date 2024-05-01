from tkinter import *
from tkinter import Canvas, Button, PhotoImage, ttk, messagebox, filedialog
from PIL import Image, ImageTk
import tkinter as tk
import cv2
import re
import threading

import ReportFrames
import UserInterface
import FaceRecFrame
import LandingFrame
import ExamConfig
import FirebaseManager
import EncodePhotos

from StudentData import *


# Class used to transition between tkinter pages
class ExamApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("ExamTrack")
        self.geometry("1200x600+20+20")
        self.resizable(False, False)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.classes = {}

        self.firebase_manager = FirebaseManager.firebase_manager

        for F in (StartPage, FaceRecFrame.FaceRec, UserInterface.UserInterface, ReportFrames.ReportFrames,
                  LandingFrame.LandingFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            self.classes[page_name] = F

            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LandingFrame")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the program?"):
            cur_exam_status = self.frames["UserInterface"].get_exam_status()
            if cur_exam_status.lower() == 'original time' or cur_exam_status.lower() == 'extra time':
                self.frames["UserInterface"].set_exam_status_finish()
            FirebaseManager.delete_cache_dir()
            self.destroy()

    def show_frame(self, page_name):
        if page_name == "FaceRec" and self.firebase_manager.get_state() == FirebaseManager.AppState.DONE:
            app.frames["FaceRec"].load_encode_file()
            self.firebase_manager.set_loaded()

        frame = self.frames[page_name]
        frame.tkraise()

    def reset_frame(self, page_name):
        if page_name == 'UserInterface':
            self.frames[page_name].destroy_child_frames()
        self.frames[page_name].destroy()
        self.frames[page_name] = self.classes[page_name](parent=self.container, controller=self)
        self.frames[page_name].grid(row=0, column=0, sticky="nsew")

    def reset_exam(self):
        students.reset_att()
        ExamConfig.cur_exam = ExamConfig.ExamConfig()
        FirebaseManager.firebase_manager.reset_att()

        self.reset_frame('StartPage')
        self.reset_frame('UserInterface')
        self.reset_frame('FaceRec')


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file="Resources/start_background.png")

        self.firebase_manager = FirebaseManager.firebase_manager
        self.encode_photos = EncodePhotos.encode_photos

        # Creating Canvas
        canvas = Canvas(
            self,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        canvas.place(x=0, y=0)

        # Upload label and picture

        self.upload_pic = tk.PhotoImage(file="Resources/upload_file.png")
        panel_upload = tk.Label(self, bd=0, cursor="hand2")
        panel_upload.place(x=950, y=480)
        panel_upload.configure(image=self.upload_pic)
        panel_upload.tkraise()

        self.confirmed_img = tk.PhotoImage(file="Resources/confirmed.png")
        confirmed_img_panel = Label(self, image=self.confirmed_img, borderwidth=0)
        # confirmed_img_panel.place(x=910,y=480)

        self.file_uploaded = False

        def remove_uploaded_file():
            self.file_uploaded = 0
            confirmed_img_panel.place_forget()
            remove_btn.place_forget()

        remove_btn = Button(self, text='Remove', bd='3', fg="#FFFFFF", bg='#812e91', font=("Calibri", 12 * -1),
                            activebackground='#917FB3', height='1', width='10', command=remove_uploaded_file)
        # remove_btn.place(x=1025, y=500)

        canvas.create_text(
            935.0,
            545.0,
            anchor="nw",
            text="Upload .csv file",
            fill="white",
            font=("Inter Bold", 15 * -1)
        )

        # Select camera
        self.cap = None
        self.selected_device = 0
        self.capture_running = False
        self.camera_waiting_small = tk.PhotoImage(file="Resources/camera_waiting_small.png")

        # Function to start capture loop
        def start_rec():
            def scan():
                success, self.img = self.cap.read()
                if success:
                    # convert to RGB
                    self.img_arr = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                    # converting to img
                    self.img = Image.fromarray(self.img_arr)
                    self.tkimg = ImageTk.PhotoImage(self.img)
                    panel.config(image=self.tkimg)
                    panel.tkimg = self.tkimg
                if self.capture_running:
                    panel.after(25, scan)  # change value to adjust FPS

            if not self.capture_running:
                self.cap = cv2.VideoCapture(self.selected_device)
                self.cap.set(3, 240 * 0.75)
                self.cap.set(4, 180 * 0.75)
                self.capture_running = True
                scan()  # start the capture loop
            else:
                print('capture already started')

        # Create the label with the image
        panel = tk.Label(self)
        panel.place(x=900, y=200)
        panel.configure(image=self.camera_waiting_small)
        panel.tkraise()

        if self.cap:
            self.cap.release()

        def pause_rec():
            self.capture_running = False
            if self.cap is not None:
                self.cap.release()
            panel.configure(image=self.camera_waiting_small)

        # Get available camera devices
        available_devices = []
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_devices.append('Camera ' + str(i))
            cap.release()

        def combo_cameras_changed(a):
            pause_rec()
            self.selected_device = int(combo_cameras.get().split()[1])

        canvas.create_text(
            795.0,
            165.0,
            anchor="nw",
            text="Select Camera:",
            fill="white",
            font=("Inter Bold", 15 * -1)
        )

        # Create ComboBox to select camera device
        combo_cameras = ttk.Combobox(self, values=available_devices, state='readonly')
        combo_cameras.place(x=900, y=165)
        self.selected_device = 0

        combo_cameras.bind("<<ComboboxSelected>>", combo_cameras_changed)

        # test camera btn
        test_btn = Button(self, text='Test', bd='3', fg="#FFFFFF", bg='#812e91', font=("Calibri", 12 * -1),
                          activebackground='#917FB3', height='1', width='10', command=start_rec)
        test_btn.place(x=950, y=360)

        # Select camera  END

        # Adding labels and entries

        canvas.create_text(
            400.0,
            150.0,
            anchor="nw",
            text="Exam Number:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        exam_entry = tk.Entry(self, width=13, bg="#917FB3", font=18, borderwidth=3)
        exam_entry.place(x=525, y=145)

        canvas.create_text(
            400.0,
            200.0,
            anchor="nw",
            text="Term:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        # creating combo box
        combo_terms = ttk.Combobox(self, state="readonly", values=['MoedA', 'MoedB', 'MoedC'],
                                   foreground="#917FB3", font=("Calibri", 18 * -1), width=10)
        combo_terms.place(x=525, y=198)

        canvas.create_text(
            400.0,
            250.0,
            anchor="nw",
            text="Duration:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        duration_entry = tk.Entry(self, width=4, bg="#917FB3", font=18, borderwidth=3)
        duration_entry.place(x=525, y=245)

        canvas.create_text(
            585.0,
            250.0,
            anchor="nw",
            text="Minutes",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        canvas.create_text(
            400.0,
            300.0,
            anchor="nw",
            text="Supervisors:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        self.supervisor_num = 2

        def exam_add_supervisor():
            self.supervisor_num += 1
            if self.supervisor_num % 4 == 1:
                supervisor_entry2.place_forget()
                supervisor_entry3.place_forget()
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 2:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place_forget()
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 3:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place(x=525, y=395)
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 0:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place(x=525, y=395)
                supervisor_entry4.place(x=525, y=445)

        def get_supervisor_list():
            sup_list = [supervisor_entry.get()]
            sup_len = self.supervisor_num % 4
            if sup_len == 0:
                sup_len = 4
            if sup_len >= 2:
                sup_list.append(supervisor_entry2.get())
            if sup_len >= 3:
                sup_list.append(supervisor_entry3.get())
            if sup_len == 4:
                sup_list.append(supervisor_entry4.get())
            return sup_list

        supervisor_entry = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        supervisor_entry.place(x=525, y=295)

        supervisor_entry2 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        supervisor_entry2.place(x=525, y=345)

        supervisor_entry3 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        # supervisor_entry3.place(x=525,y=445)

        supervisor_entry4 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        # supervisor_entry.place(x=525,y=495)

        add_sup_btn = Button(self, text='+', bd='3', fg="#FFFFFF", bg='#812e91', font=("Arial", 16 * -1),
                             activebackground='#917FB3', height='1', width='2', command=exam_add_supervisor)
        add_sup_btn.place(x=770, y=295)

        def upload_csv_file(a):
            # Open file dialog to select CSV file
            filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if filepath:
                # Read the selected CSV file
                res = students.read_students_csv(filepath)
                if not res:
                    messagebox.showerror("Exam Error", "Failed to upload file.")
                    return False
                if not students.check_csv_struct():
                    messagebox.showerror("Exam Error", "Uploaded file structure does not match.")
                    return False
                self.file_uploaded = True
                confirmed_img_panel.place(x=910, y=480)
                remove_btn.place(x=1025, y=500)

        def check_supervisor_name(str_name):
            # Use regular expression to check if the entry consists only of letters and whitespace
            if re.match(r'^[a-zA-Z\s]+$', str_name):
                # Split the entry into words
                words = str_name.split()
                # Check if the number of words is at least two
                if len(words) >= 2:
                    return True
            return False

        # Handling input correctness check
        def check_entry_correctness():
            error_list = []
            error_flag, sup_error_flag = 0, 0

            if not exam_entry.get().isdigit():
                error_flag += 1
                error_list.append('Invalid exam number.')

            if len(combo_terms.get()) < 3:
                error_flag += 1
                error_list.append('Please select term.')

            exam_dur = duration_entry.get()
            if not exam_dur.isdigit() or int(exam_dur) < 30:
                error_flag += 1
                error_list.append('Invalid duration.')

            sup_num = self.supervisor_num % 4
            if not check_supervisor_name(supervisor_entry.get()):
                sup_error_flag = 1
            elif sup_num == 2 and not check_supervisor_name(supervisor_entry2.get()):
                sup_error_flag = 1
            elif sup_num == 3 and not check_supervisor_name(supervisor_entry3.get()):
                sup_error_flag = 1
            elif sup_num == 0 and not check_supervisor_name(supervisor_entry4.get()):
                sup_error_flag = 1

            if sup_error_flag:
                error_flag += 1
                error_list.append('Invalid supervisor name')

            if error_flag > 0:
                error_message = "Invalid Input:\n"
                for error in error_list:
                    error_message += f"- {error}\n"
                messagebox.showerror("Input Error", error_message)

            return error_flag

        # continue functionality

        def starting_frame_continue():
            if check_entry_correctness() != 0:  # Check input
                return
            if not self.file_uploaded:  # CSV file was not manually upload
                res = self.firebase_manager.get_csv_file(exam_entry.get(), combo_terms.get())
                if res != True:
                    messagebox.showerror(res[0], res[1])
                    return
            # Set Exam Config
            ExamConfig.cur_exam.set_all(exam_entry.get(), int(duration_entry.get()), combo_terms.get(),
                                        get_supervisor_list(), self.selected_device)

            app.frames["UserInterface"].initiate_table()
            app.frames["UserInterface"].initiate_time()

            FirebaseManager.delete_cache_dir()  # Delete existing Cache folder if existing

            # Thread to allow the app to run while downloading images
            fetch_thread = threading.Thread(target=lambda: self.download_and_encode())
            fetch_thread.start()

            controller.show_frame("UserInterface")
            # print(ExamConfig.cur_exam.__dict__)

        # continue btn
        continue_btn = Button(self, text='Continue', bd='5', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                              activebackground='#917FB3', height='1', width='14', command=starting_frame_continue)
        continue_btn.place(x=500, y=515)

        back_btn = tk.Button(self, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.controller.show_frame("LandingFrame")])
        back_btn.place(x=30, y=30)

        # Bind the label to the label_clicked function when clicked
        panel_upload.bind("<Button-1>", upload_csv_file)

    # Cache images using thread
    def download_and_encode(self):
        self.firebase_manager.cache_files_from_firebase(FirebaseManager.CACHE_FOLDER_DOWNLOAD)

        self.firebase_manager.set_encoding()
        self.encode_photos.create_img_list()
        self.encode_photos.find_encodings()
        if not self.encode_photos.encode_images():
            self.firebase_manager.set_failed()
            return

        self.firebase_manager.set_done()


app = ExamApp()
app.mainloop()
