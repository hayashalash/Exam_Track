from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
from datetime import date, datetime
import threading

from StudentData import *
import ReportData

import ExamConfig
import FirebaseManager

import BreaksFeature
import NotesFeature
import ManualConfirmFeature


# Loading label, changes according to the state of the app - enables face recognition button when done
class LoadingLabel:
    def __init__(self, frame, canvas, label_ref, text):
        self.frame = frame
        self.label_ref = label_ref
        self.canvas = canvas
        self.text = text
        self.rotation_chars = ["|", "/", "-", "\\"]
        self.rotation_index = 0
        self.update_text()

    def update_text(self):
        temp_state = FirebaseManager.firebase_manager.get_state()
        rot = self.rotation_chars[self.rotation_index]
        loading_text = self.text + " " + rot + " " + rot + " " + rot

        if temp_state == FirebaseManager.AppState.ENCODING or temp_state == FirebaseManager.AppState.DOWNLOADING:
            self.text = str(self.frame.firebase_manager.get_state().value)
            self.rotation_index = (self.rotation_index + 1) % len(self.rotation_chars)
            self.canvas.itemconfig(self.label_ref, text=loading_text)
        elif temp_state == FirebaseManager.AppState.FAILED:
            self.canvas.itemconfig(self.label_ref, text="Failed")
            self.frame.show_retry_btn()
        elif temp_state == FirebaseManager.AppState.DONE:
            self.canvas.itemconfig(self.label_ref, text="")
            self.frame.enable_face_recognition()
            return

        self.canvas.after(350, self.update_text)  # Update every given milliseconds


class UserInterface(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.y_scrollbar = None
        self.controller = controller
        self.parent = parent
        self.bgimg = tk.PhotoImage(file="Resources/interface_background.png")
        self.manual_confirm = ManualConfirmFeature.ManualConfirm()
        self.notes_features = NotesFeature.NotesFeature()
        self.breaks_feature = BreaksFeature.BreaksFeature()

        self.firebase_manager = FirebaseManager.firebase_manager
        self.exam = ExamConfig.cur_exam

        # Creating Cancvas
        self.canvas = Canvas(self, bg="#2A2F4F", height=600, width=1200, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        self.canvas.place(x=0, y=0)

        self.canvas.create_rectangle(895, 225, 1000, 380, fill='#917FB3', outline='black')

        # Loading Label

        self.loading_label = self.canvas.create_text(
            960.0,
            40.0,
            anchor="nw",
            text="00:00",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        LoadingLabel(self, self.canvas, self.loading_label, 'Downloading')

        # Creating Profile

        self.profile_gui = tk.PhotoImage(file="Resources/profile_ui2.png")
        self.canvas.create_image(20, 20, anchor=NW, image=self.profile_gui)

        self.profile_pic_frame_tk = tk.PhotoImage(file="Resources/pic_frame.png")
        self.canvas.create_image(58, 58, anchor=NW, image=self.profile_pic_frame_tk)

        self.profile_pic_tk = tk.PhotoImage(file="Resources/no_pic.png")
        profile_pic = self.canvas.create_image(60, 60, anchor=NW, image=self.profile_pic_tk)

        self.confirmed_img = tk.PhotoImage(file="Resources/confirmed.png")
        confirmed_img_panel = Label(self, image=self.confirmed_img, borderwidth=0)
        # confirmed_img_panel.place(x=250,y=422)

        self.not_confirmed_img = tk.PhotoImage(file="Resources/not_confirmed.png")
        not_confirmed_img_panel = Label(self, image=self.not_confirmed_img, borderwidth=0)
        # not_confirmed_img_panel.place(x=250,y=422)

        extra_img_panel = Label(self, image=self.confirmed_img, borderwidth=0)
        # extra_img_panel.place(x=90,y=422)
        no_extra_img_panel = Label(self, image=self.not_confirmed_img, borderwidth=0)

        # adding labels
        student_name_label = self.canvas.create_text(
            115.0,
            295.0,
            anchor="nw",
            text="(Name)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_id_label = self.canvas.create_text(
            115.0,
            335.0,
            anchor="nw",
            text="(ID)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = self.canvas.create_text(
            115.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="(Major)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_confirmed_label = self.canvas.create_text(
            253.0,
            427.0,
            justify=CENTER,
            anchor="nw",
            text="",
            fill="#FFFFFF",
            font=("Calibri Bold", 20 * -1)
        )

        self.canvas.create_text(
            42.0,
            458.0,
            justify=CENTER,
            anchor="nw",
            text="Extra Time",
            fill="#FFFFFF",
            font=("Calibri", 12 * -1)
        )

        self.canvas.create_text(
            197.0,
            458.0,
            justify=CENTER,
            anchor="nw",
            text="Attendance",
            fill="#FFFFFF",
            font=("Calibri", 12 * -1)
        )

        # Create Table
        # table_columns = student_table_columns()
        # Create a Frame to contain the Treeview
        self.table_frame = ttk.Frame(self, borderwidth=2)
        self.table_frame.place(x=360, y=130)

        self.table = ttk.Treeview(master=self.table_frame)
        # table.place(x=360, y=150, height=260)

        self.table.tag_configure('oddrow', background='#917FB3')
        self.table.tag_configure('evenrow', background='#BAA4CA')

        '''# Create a vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=table.yview)
        scrollbar.place(x=850, y=140, height=250)

        # Configure the table to use the scrollbar
        table.configure(yscrollcommand=scrollbar.set)'''

        # Selecting row in table

        self.img_holder = tk.PhotoImage(file="Resources/no_pic.png")
        self.current_id = ""

        # enabled/disabled relevant button depending on the students attendance
        def set_button_state(str_state):
            if str_state == "submitted":
                confirm_btn["state"] = "disabled"
                break_btn["state"] = "disabled"
                view_breaks_btn["state"] = "disabled"

                self.submit_btn.place_forget()
                self.undo_submit_btn.place(x=535, y=520)

                if self.exam.is_waiver_available():
                    self.undo_waiver_btn.place_forget()
                    self.waiver_btn.place(x=700, y=470)
                    self.waiver_btn["state"] = "disabled"

            elif str_state == "waiver":
                confirm_btn["state"] = "disabled"
                break_btn["state"] = "disabled"
                view_breaks_btn["state"] = "disabled"

                self.submit_btn.place(x=535, y=520)
                self.undo_submit_btn.place_forget()
                self.submit_btn["state"] = "disabled"

                self.undo_waiver_btn.place(x=700, y=470)
                self.waiver_btn.place_forget()
                # self.waiver_btn["state"] = "normal"

            elif str_state == "confirmed":
                confirm_btn["state"] = "disabled"
                break_btn["state"] = "normal"
                view_breaks_btn["state"] = "normal"

                self.submit_btn["state"] = "normal"
                self.submit_btn.place(x=535, y=520)
                self.undo_submit_btn.place_forget()

                if self.exam.is_waiver_available():
                    self.undo_waiver_btn.place_forget()
                    self.waiver_btn.place(x=700, y=470)
                    self.waiver_btn["state"] = "normal"

            elif str_state == "not_confirmed":
                confirm_btn["state"] = "normal"
                break_btn["state"] = "disabled"
                view_breaks_btn["state"] = "disabled"

                self.submit_btn["state"] = "disabled"
                self.submit_btn.place(x=535, y=520)
                self.undo_submit_btn.place_forget()

                if self.exam.is_waiver_available():
                    self.undo_waiver_btn.place_forget()
                    self.waiver_btn.place(x=700, y=470)
                    self.waiver_btn["state"] = "disabled"

        def table_select_row(a):  # view selected row items
            cur_item = self.table.focus()
            cur_values = self.table.item(cur_item, option='values')  # this option keeps ID as string
            if not cur_values:
                return
            # cur_values = table.item(cur_item)['values'] # this option converts ID into integer
            self.current_id = str(cur_values[0])
            self.canvas.itemconfig(student_id_label, text=str(self.current_id))
            self.canvas.itemconfig(student_name_label, text=students.student_get_name(self.current_id))

            temp_extra_time = students.student_get_extra_time(self.current_id)
            if temp_extra_time.lower() == "no":
                no_extra_img_panel.place(x=90, y=422)
                extra_img_panel.place_forget()
            else:
                no_extra_img_panel.place_forget()
                extra_img_panel.place(x=90, y=422)

            self.canvas.itemconfig(student_major_label, text=students.student_get_major(self.current_id))

            if students.student_check_submit(self.current_id):
                set_button_state("submitted")
                confirmed_img_panel.place(x=250, y=422)
                not_confirmed_img_panel.place_forget()
            elif students.student_check_waiver(self.current_id):
                set_button_state("waiver")
                self.canvas.itemconfig(student_confirmed_label, text="Waiver", fill='#b83e4f')
                confirmed_img_panel.place_forget()
                not_confirmed_img_panel.place_forget()
            elif students.student_check_attendance(self.current_id):
                set_button_state("confirmed")
                self.canvas.itemconfig(student_confirmed_label, text="")
                confirmed_img_panel.place(x=250, y=422)
                not_confirmed_img_panel.place_forget()
            else:
                set_button_state("not_confirmed")
                self.canvas.itemconfig(student_confirmed_label, text="")
                confirmed_img_panel.place_forget()
                not_confirmed_img_panel.place(x=250, y=422)

            if students.student_in_break(self.current_id):
                break_btn.place_forget()
                back_from_break_btn.place(x=535, y=420)
            else:
                back_from_break_btn.place_forget()
                break_btn.place(x=535, y=420)

            self.img_holder = tk.PhotoImage(file=FirebaseManager.get_image_path(self.current_id))
            self.canvas.itemconfig(profile_pic, image=self.img_holder)
            # Fetch blob using threading
            '''fetch_thread = threading.Thread(target=fetch_blob)
            fetch_thread.start()'''

        self.table.bind("<<TreeviewSelect>>", table_select_row)

        # Searching the table

        self.canvas.create_text(
            895,
            150,
            anchor="nw",
            text="Search ID:",
            fill="#FFFFFF",
            font=("Calibri Bold", 18 * -1)
        )

        search_entry = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        search_entry.place(x=895, y=185)

        # Search query and filter table
        def my_search(*args):
            table_df = students.get_student_df_ref()
            query = search_entry.get().strip()  # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            self.table.delete(*self.table.get_children())
            j = 0  # similar to color j , counter for colouring purpose
            for dt in r_set:
                tags = ('evenrow',) if j % 2 == 0 else ('oddrow',)  # for colouring purpose
                v = [r for r in dt]  # creating a list from each row
                # Handling checkbox statuses
                s_id = v[0]
                if confirmed_checkbox_var.get() == 1 and extra_checkbox_var.get() == 0:
                    if students.student_check_attendance(s_id):
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                        j += 1  # colouring
                elif confirmed_checkbox_var.get() == 1 and extra_checkbox_var.get() == 1:
                    if students.student_check_attendance(s_id) and students.student_get_extra_time(
                            s_id).lower() == 'yes':
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                        j += 1  # colouring
                elif confirmed_checkbox_var.get() == 0 and extra_checkbox_var.get() == 1:
                    if students.student_get_extra_time(s_id).lower() == 'yes':
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                        j += 1  # colouring
                else:
                    self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                    j += 1  # colouring

        search_entry.bind("<KeyRelease>", my_search)

        # Checkboxes
        confirmed_checkbox_var = IntVar()
        confirmed_checkbox = Checkbutton(self, variable=confirmed_checkbox_var, onvalue=1, offvalue=0, height=1,
                                         font=("Inter Bold", 14 * -1), text="Attending", bg="#917FB3",
                                         command=my_search)
        confirmed_checkbox.place(x=900, y=230)

        extra_checkbox_var = IntVar()
        extra_checkbox = Checkbutton(self, variable=extra_checkbox_var, onvalue=1, offvalue=0, height=1,
                                     font=("Inter Bold", 14 * -1), text="Extra time", bg="#917FB3",
                                     command=my_search)
        extra_checkbox.place(x=900, y=260)

        def filter_students(checkbox_name):
            table_df = students.get_student_df_ref()
            checkboxes = {
                'break': (break_checkbox_var, break_checkbox),
                'waiver': (waiver_checkbox_var, waiver_checkbox),
                'submit': (submit_checkbox_var, submit_checkbox),
                'extra': (extra_checkbox_var, extra_checkbox),
                'confirmed': (confirmed_checkbox_var, confirmed_checkbox)
            }

            checkbox_var, checkbox = checkboxes[checkbox_name]

            if checkbox_var.get() == 1:
                for other_checkbox_name, (other_checkbox_var, other_checkbox) in checkboxes.items():
                    if other_checkbox_name != checkbox_name:
                        other_checkbox_var.set(0)
                        other_checkbox.configure(state="disabled")
            else:
                for other_checkbox_name, (other_checkbox_var, other_checkbox) in checkboxes.items():
                    # other_checkbox_var.set(1)
                    other_checkbox.configure(state="normal")

            query = search_entry.get().strip()  # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            self.table.delete(*self.table.get_children())
            color_i = 0
            for dt in r_set:
                v = [r for r in dt]  # creating a list from each row
                j_tags = ('evenrow',) if color_i % 2 == 0 else ('oddrow',)
                if checkbox_name == 'break' and checkbox_var.get() == 1:
                    if students.student_in_break(v[0]):
                        self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                        color_i += 1
                elif checkbox_name == 'waiver' and checkbox_var.get() == 1:
                    if students.student_check_waiver(v[0]):
                        self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                        color_i += 1
                elif checkbox_name == 'submit' and checkbox_var.get() == 1:
                    if students.student_check_submit(v[0]):
                        self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                        color_i += 1
                else:
                    self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                    color_i += 1

        break_checkbox_var = IntVar()
        break_checkbox = Checkbutton(self, variable=break_checkbox_var, onvalue=1, offvalue=0, height=1,
                                     font=("Inter Bold", 14 * -1), text="On Break", bg="#917FB3",
                                     command=lambda: filter_students('break'))
        break_checkbox.place(x=900, y=290)

        waiver_checkbox_var = IntVar()
        waiver_checkbox = Checkbutton(self, variable=waiver_checkbox_var, onvalue=1, offvalue=0, height=1,
                                      font=("Inter Bold", 14 * -1), text="Waiver", bg="#917FB3",
                                      command=lambda: filter_students('waiver'))
        waiver_checkbox.place(x=900, y=320)

        submit_checkbox_var = IntVar()
        submit_checkbox = Checkbutton(self, variable=submit_checkbox_var, onvalue=1, offvalue=0, height=1,
                                      font=("Inter Bold", 14 * -1), text="Submitted", bg="#917FB3",
                                      command=lambda: filter_students('submit'))
        submit_checkbox.place(x=900, y=350)

        # Timers

        # time variables
        self.waiver_available = self.exam.is_waiver_available()
        self.extra_time_flag = 0
        self.waiver_total_seconds = 15
        self.total_seconds = 30

        self.time_secs_extra = 5

        self.exam_status = 'IDLE'

        # Creating original timer labels
        time_note_label = self.canvas.create_text(
            525.0,
            55.0,
            anchor="nw",
            text="Time Left",
            fill="#FFFFFF",
            font=("Inter Bold", 12 * -1)
        )
        self.time_label = self.canvas.create_text(
            525.0,
            73.0,
            anchor="nw",
            text="00:00",
            fill="#FFFFFF",
            font=("Arial", 15, "",)
        )

        # Creating Waiver labels
        self.waiver_label = self.canvas.create_text(
            425.0,
            55.0,
            anchor="nw",
            text="Waiver Time",
            fill="#FFFFFF",
            font=("Inter Bold", 12 * -1)
        )
        self.waiver_time_label = self.canvas.create_text(
            430.0,
            73.0,
            anchor="nw",
            text=str(ExamConfig.WAIVER_TIME) + ":00",
            fill="#FFFFFF",
            font=("Arial", 15, "",)
        )
        bbox2 = self.canvas.bbox(self.waiver_time_label)
        self.rect_item2 = self.canvas.create_rectangle(bbox2, outline="purple")
        self.canvas.tag_raise(self.waiver_time_label, self.rect_item2)

        def countdown():
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            if self.total_seconds >= 0:
                self.canvas.itemconfig(self.time_label, text="{:02d}:{:02d}".format(minutes, seconds))
                self.after(1000, countdown)
                self.total_seconds -= 1
            else:
                if self.extra_time_flag:
                    messagebox.showinfo("Time Countdown", "Extra time is over.")
                    self.set_exam_status_finish()
                    add_time_btn.place_forget()
                else:
                    messagebox.showinfo("Time Countdown", "Original time is over.")
                    self.canvas.itemconfig(time_note_label, text="Extra Time")
                    self.extra_time_flag = 1
                    self.total_seconds = self.time_secs_extra
                    self.exam_status = 'Extra Time'
                    countdown()

        def waiver_countdown():
            waiver_minutes = self.waiver_total_seconds // 60
            waiver_seconds = self.waiver_total_seconds % 60
            if self.waiver_total_seconds >= 0:
                self.canvas.itemconfig(self.waiver_time_label,
                                       text="{:02d}:{:02d}".format(waiver_minutes, waiver_seconds))
                self.after(1000, waiver_countdown)
                self.waiver_total_seconds -= 1
            else:
                messagebox.showinfo("Time Countdown", "Waiver time is over.")

        def start_countdown():
            start_btn["state"] = "disabled"
            add_time_btn.place(x=595, y=67)
            self.exam_status = 'Original Time'
            self.send_exam_status()
            countdown()
            if self.waiver_available:
                waiver_countdown()

        # start exams/timers button
        start_btn = Button(self, text='Start Exam', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                           activebackground='#917FB3', height='1', width='14', command=start_countdown,
                           disabledforeground='gray')
        start_btn.place(x=700, y=60)

        # Add Time for exam

        def add_time():
            add_time_window = Toplevel(self)
            add_time_window.geometry("300x270+350+200")
            add_time_window.resizable(False, False)
            add_time_window.title("Add Time")
            add_time_window.configure(bg='#917FB3')
            add_time_window_reason = Label(add_time_window, text="Specify Reason:",
                                           bg='#917FB3', font=("Calibri", 16 * -1))
            add_time_window_reason.place(x=20, y=70)

            add_time_label = Label(add_time_window, text="Add minutes:",
                                   bg='#917FB3', font=("Calibri", 16 * -1))
            add_time_label.place(x=20, y=30)

            add_time_box = Spinbox(add_time_window, from_=0, to=100, increment=5, font=("Calibri", 16 * -1), width=3)
            add_time_box.place(x=120, y=30)

            add_reason_entry = scrolledtext.ScrolledText(add_time_window, wrap=tk.WORD, bd=3, bg='#E5BEEC', width=30,
                                                         height=3, font=("Calibri", 16 * -1))
            add_reason_entry.place(x=20, y=95)

            # add minute to time variable
            def add_total_seconds():
                temp_added = int(add_time_box.get())
                self.total_seconds += temp_added * 60
                self.exam.add_time(temp_added)
                add_time_window.destroy()

            # Buttons
            add_time_confirm_btn = Button(add_time_window, text='Confirm', bd='4', fg="#FFFFFF", bg='#812e91',
                                          font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                                          disabledforeground='gray', command=add_total_seconds)
            add_time_confirm_btn.place(x=30, y=200)

            add_time_cancel_btn = Button(add_time_window, text='Cancel', bd='4', fg="#FFFFFF", bg='#812e91',
                                         font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                                         disabledforeground='gray', command=add_time_window.destroy)
            add_time_cancel_btn.place(x=145, y=200)

        # add time button
        add_time_btn = Button(self, text='+', bd='3', fg="#FFFFFF", bg='#812e91', font=("Arial", 13 * -1),
                              activebackground='#917FB3', height='1', width='2', command=add_time)

        # add_time_btn.place(x = 590,y = 80)

        # retry button - only shows in case the encoding fails
        def retry_download_encode():
            self.firebase_manager.set_downloading()
            self.retry_btn.place_forget()  # hide button when clicked
            # Thread to allow the app to run while downloading images
            fetch_thread = threading.Thread(target=lambda: controller.frames["StartPage"].download_and_encode())
            fetch_thread.start()

        self.retry_btn = Button(self, text='Retry', bd='4', fg="#FFFFFF", bg='#812e91',
                                activebackground='#917FB3', font=("Calibri", 12 * -1), height='1', width='10'
                                , command=retry_download_encode)
        # self.retry_btn.place(x = 1100,y = 40)

        # open face recognition frame
        self.face_recognition_btn = Button(self, text='Face Recognition', bd='4', fg="#FFFFFF", bg='#812e91',
                                           activebackground='#917FB3', font=("Calibri", 16 * -1), height='1', width='14'
                                           , command=lambda: [controller.show_frame("FaceRec")], state="disabled")

        self.face_recognition_btn.place(x=950, y=80)

        # confirm manually
        def manual_confirm_check(student_id):  # check before calling manual confirm
            if students.student_check_attendance(student_id):
                messagebox.showwarning("Manual Confirm Message", "Student attendance already confirmed.")
                return
            self.manual_confirm.confirm_popup(self.parent, self.current_id)

        confirm_btn = Button(self, text='Manual Confirm', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                             command=lambda: manual_confirm_check(self.current_id))
        confirm_btn.place(x=700, y=420)

        # Interface add notes button
        add_notes_btn = Button(self, text='Add Notes', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: self.notes_features.add_note_popup(self.parent, self.current_id))
        add_notes_btn.place(x=360, y=420)

        # View Notes

        # Interface view notes button

        # open view notes window only if student has notes
        def popup_notes_exist(req_id):
            ref = self.firebase_manager.get_student_notes(req_id)
            if ref.get():
                self.notes_features.view_note_popup(self.parent, req_id)
            else:
                messagebox.showinfo("View Notes Message", "Student has no notes.")

        # View notes button
        view_notes_btn = Button(self, text='View Notes', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                                activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                command=lambda: popup_notes_exist(self.current_id))
        view_notes_btn.place(x=360, y=470)

        self.last_hover_time = datetime.now()

        # refresh to display updated info on ui
        def table_selection_refresh(a):
            current_time = datetime.now()
            if (current_time - self.last_hover_time).total_seconds() >= 5:
                selected_item = self.table.selection()  # Get the currently selected item
                self.table.selection_set(selected_item)  # Reselect the same item
                self.last_hover_time = current_time

        self.bind("<Enter>", table_selection_refresh)

        # Break Function
        def student_take_break(student_id):
            if not students.student_check_attendance(student_id):
                messagebox.showerror("Break Error", "Student not in attendance.")
                return
            if students.student_in_break(student_id):
                messagebox.showerror("Break Error", "Student already in break.")
                return
            self.breaks_feature.break_window(self.parent, self.current_id)

        # Break features buttons
        break_btn = Button(self, text='Break', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                           activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                           command=lambda: student_take_break(self.current_id))
        break_btn.place(x=535, y=420)

        # Back from break check function
        def student_back_from_break(student_id):
            if not students.student_check_attendance(student_id):
                messagebox.showerror("Break Error", "Student attendance was not confirmed.")
                return
            if not students.student_in_break(student_id):
                messagebox.showinfo("Break Info", "Student not in break.")
                return
            res = students.student_back_break(self.current_id)
            if res != STUDENT_NOT_FOUND:
                messagebox.showinfo("Break Info", res)
                if break_checkbox_var.get() == 1:
                    filter_students('break')
                else:
                    my_search()

        # back from break button
        back_from_break_btn = Button(self, text='Back from Break', bd='4', fg="#FFFFFF", bg='#812e91',
                                     font=("Calibri", 16 * -1),
                                     activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                     command=lambda: student_back_from_break(self.current_id))
        # back_btn.place(x = 535,y = 480)

        # view breaks btn

        view_breaks_btn = Button(self, text='View Breaks', bd='4', fg="#FFFFFF", bg='#812e91',
                                 font=("Calibri", 16 * -1),
                                 activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                 command=lambda: self.breaks_feature.view_break_window(self.parent, self.current_id))
        view_breaks_btn.place(x=535, y=470)

        # waiver
        def student_waiver_popup(student_id):
            if students.student_report_waiver(student_id) != FUNC_SUCCESS:
                messagebox.showerror("Waiver Error", "Student not found.")
                return
            self.waiver_btn.place_forget()
            self.undo_waiver_btn.place(x=700, y=470)
            messagebox.showinfo("Waiver Message", "Student waiver successful.")

        def student_undo_waiver(student_id):
            res = students.student_undo_waiver(student_id)
            if res == STUDENT_NOT_FOUND:
                messagebox.showerror("Undo Waiver Error", "Student not found.")
                return
            if res == STUDENT_ALREADY_CONFIRMED:
                messagebox.showerror("Undo Waiver Error", "Student is already attending.")
                return
            messagebox.showinfo("Waiver Message", "Undo waiver successful.")
            filter_students('waiver')
            self.waiver_btn.place(x=700, y=470)
            self.undo_waiver_btn.place_forget()

        # waiver button
        self.waiver_btn = Button(self, text='Waiver', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                                 activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                 command=lambda: student_waiver_popup(self.current_id))
        self.waiver_btn.place(x=700, y=470)
        if not self.exam.is_waiver_available():  # Show waiver btn only if waiver option is available
            self.waiver_btn["state"] = "disabled"

        # undo waiver button
        self.undo_waiver_btn = Button(self, text='Undo Waiver', bd='4', fg="#FFFFFF", bg='#812e91',
                                      font=("Calibri", 16 * -1),
                                      activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                      command=lambda: student_undo_waiver(self.current_id))
        # self.undo_waiver_btn.place(x=700, y=470)

        # View Report
        self.view_report_btn = Button(self, text='View Report', bd='4', fg="#FFFFFF", bg='#812e91',
                                      activebackground='#917FB3', font=("Calibri", 16 * -1), height='1', width='14'
                                      , command=lambda: [controller.frames["ReportFrames"].create_report(False),
                                                         controller.show_frame("ReportFrames")])

        self.view_report_btn.place(x=950, y=470)

        def exit_popup():
            exit_window = Toplevel(self)
            exit_window.geometry("300x230+350+100")
            exit_window.resizable(False, False)
            exit_window.title("Exit Exam")
            exit_window.configure(bg='#917FB3')

            exit_window_text_area = scrolledtext.ScrolledText(exit_window, wrap=tk.WORD, bd=3, background="#E5BEEC",
                                                              width=25, height=3, font=("Calibri", 16 * -1))

            exit_window_specify = Label(exit_window, text="You are about to cancel the exam.\nPlease specify reason:",
                                        bg='#917FB3', font=("Calibri", 16 * -1))
            exit_window_specify.place(x=30, y=20)
            exit_window_text_area.place(x=30, y=70)

            self.str_reason = ""

            def exit_submit_event():
                self.str_reason = exit_window_text_area.get("1.0", END).strip()
                if len(self.str_reason) < 3:
                    messagebox.showerror("Manual Confirm Error", "Invalid Reason", parent=exit_window)
                else:
                    self.set_exam_status_finish()
                    self.controller.reset_exam()
                    self.controller.show_frame('LandingFrame')
                    exit_window.destroy()

            # Buttons
            e_confirm_btn = Button(exit_window, text='Confirm', bd='5', fg="#FFFFFF", bg='#812e91',
                                   font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                                   disabledforeground='gray', command=lambda: exit_submit_event())
            e_confirm_btn.place(x=30, y=160)

            e_cancel_btn = Button(exit_window, text='Cancel', bd='5', fg="#FFFFFF", bg='#812e91',
                                  font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                                  disabledforeground='gray', command=exit_window.destroy)
            e_cancel_btn.place(x=145, y=160)

        # Exit Exam
        self.exit_btn = Button(self, text='Exit to Menu', bd='4', fg="#FFFFFF", bg='#812e91',
                               activebackground='#917FB3', font=("Calibri", 14 * -1), height='1', width='12'
                               , command=lambda: [exit_popup()])

        self.exit_btn.place(x=10, y=10)

        # Submit functionality
        def student_submit_popup(student_id):
            if students.student_submit_exam(student_id) != FUNC_SUCCESS:
                messagebox.showerror("Submit Error", "Student not found.")
                return
            self.submit_btn.place_forget()
            self.undo_submit_btn.place(x=535, y=520)
            messagebox.showinfo("Submit Message", "Student submitted exam successfully.")

        def student_undo_submit(student_id):
            res = students.student_undo_submit(student_id)
            if res == STUDENT_NOT_FOUND:
                messagebox.showerror("Undo Submit Error", "Student not found.")
                return
            if res == STUDENT_ALREADY_CONFIRMED:
                messagebox.showerror("Undo Submit Error", "Student is already attending.")
                return
            messagebox.showinfo("Undo Submit Message", "Undo Submit successful.")
            filter_students('submit')
            self.submit_btn.place(x=535, y=520)
            self.undo_submit_btn.place_forget()

        # Submit buttons
        self.submit_btn = Button(self, text='Submit Exam', bd='4', fg="#FFFFFF", bg='#812e91',
                                 font=("Calibri", 16 * -1),
                                 activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                 command=lambda: student_submit_popup(self.current_id))
        self.submit_btn.place(x=535, y=520)

        # Undo submit buttons
        self.undo_submit_btn = Button(self, text='Undo Submit', bd='4', fg="#FFFFFF", bg='#812e91',
                                      font=("Calibri", 16 * -1),
                                      activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                      command=lambda: student_undo_submit(self.current_id))
        # undo_submit_btn.place(x=535, y=520)

    def initiate_time(self):
        self.waiver_available = self.exam.is_waiver_available()
        self.extra_time_flag = 0
        self.waiver_total_seconds = ExamConfig.WAIVER_TIME * 60
        self.total_seconds = self.exam.get_exam_duration() * 60
        self.time_secs_extra = int(ExamConfig.EXTRA_TIME_PERCENTAGE * self.total_seconds)

        self.canvas.itemconfig(self.time_label, text=str(self.exam.get_exam_duration()) + ":00")

        if not self.waiver_available:  # do not show waiver timer if not available
            self.canvas.itemconfig(self.waiver_label, text="")
            self.canvas.itemconfig(self.waiver_time_label, text="")
            self.canvas.create_text(
                370.0,
                75.0,
                anchor="nw",
                text="No Waiver Option",
                fill="#FFFFFF",
                font=("Inter Bold", 14 * -1)
            )
            self.canvas.itemconfig(self.rect_item2, state="hidden")

    def initiate_table(self):
        students.students_initiate_attendance()
        table_columns = students.student_table_columns()
        self.table.configure(columns=table_columns, show="headings")
        for column in table_columns:
            self.table.heading(column=column, text=column)
            if column == "major":
                self.table.column(column=column, width=140)
            elif column == 'tuition':
                self.table.column(column=column, width=50)
            elif column == 'extra_time':
                self.table.column(column=column, width=60)
            else:
                self.table.column(column=column, width=80)

        color_j = 0
        table_data = students.student_table_values()
        for row_data in table_data:
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            self.table.insert(parent="", index="end", values=row_data, tags=color_tags)
            color_j += 1

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, background="#917FB3", fieldbackground="#917FB3", foreground="white",
                        font=("Calibri", 14 * -1))
        style.configure("Treeview.Heading", rowheight=30, background="#917FB3", fieldbackground="#917FB3",
                        foreground="white", font=("Calibri", 14 * -1))
        style.map("Treeview.Heading", background=[("active", "#917FB3"), ("!active", "#917FB3")],
                  foreground=[("active", "white"), ("!active", "white")])
        style.map("Treeview", background=[("selected", "#000080")])

        # Create a vertical scrollbar
        self.y_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)

        # Configure the Treeview to use the scrollbar
        self.table.configure(yscrollcommand=self.y_scrollbar.set)

        self.table["height"] = 8

        self.table.pack(side="left", fill="both", expand=True)
        self.y_scrollbar.pack(side="right", fill="y")

    # Update exam status in firebase every 60 Seconds
    def send_exam_status(self):
        time_text = self.canvas.itemcget(self.time_label, "text")  # Get the text of the Canvas text item
        minutes_str = time_text.split(':')[0]  # Extract the minutes part before the colon
        minutes_int = int(minutes_str)
        status_report = ReportData.ReportData()
        status_report.create_new_report()
        status_report.update_exam_status(minutes_int, students.get_students_currently_attending(),
                                         self.exam_status)

        if self.exam_status == 'Finished':
            return

        self.after(60000, self.send_exam_status)

    def enable_face_recognition(self):
        self.face_recognition_btn["state"] = 'normal'

    def get_exam_status(self):
        return self.exam_status

    def set_exam_status_finish(self):
        self.exam_status = 'Finished'
        self.send_exam_status()

    def show_retry_btn(self):
        self.retry_btn.place(x=1100, y=40)

    def destroy_child_frames(self):
        self.table_frame.destroy()
