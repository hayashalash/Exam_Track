from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
from datetime import date, datetime

import FirebaseManager
import ExamConfig
from StudentData import *


class NotesFeature:

    def __init__(self):
        self.firebase_manager = FirebaseManager.firebase_manager

    # Add Notes Window
    def add_note_popup(self, parent, noted_id):
        if len(noted_id) == 0:
            return
        note_window = Toplevel(parent)
        note_window.geometry("400x500+350+100")
        note_window.resizable(False, False)
        note_window.title("Add Note")
        note_window.configure(bg='#917FB3')
        note_window_id_label = Label(note_window, text="Student ID:", bg='#917FB3', font=("Calibri", 16 * -1))
        note_window_id_label.place(x=30, y=30)
        note_window_id_label2 = Label(note_window, text=noted_id, bg='#917FB3', font=("Calibri", 16 * -1),
                                      borderwidth=3, relief="ridge")
        note_window_id_label2.place(x=120, y=30)

        note_window_reporter_label = Label(note_window, text="Reporter:", bg='#917FB3', font=("Calibri", 16 * -1))
        note_window_reporter_label.place(x=30, y=70)

        combo_reporter = ttk.Combobox(note_window, state="readonly", background="gray", font=("Calibri", 16 * -1),
                                      values=ExamConfig.cur_exam.get_exam_supervisors())
        combo_reporter.place(x=120, y=70)

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        note_window_date_label = Label(note_window, text=d1, bg='#917FB3', font=("Calibri", 16 * -1),
                                       borderwidth=3, relief="ridge")
        note_window_date_label.place(x=300, y=5)

        note_window_subject_label = Label(note_window, text="Subject:", bg='#917FB3', font=("Calibri", 16 * -1))
        note_window_subject_label.place(x=30, y=110)
        note_window_subject_entry = Entry(note_window, bg='#E5BEEC', bd=3, font=("Calibri", 16 * -1))
        note_window_subject_entry.place(x=120, y=110)

        note_window_note_label = Label(note_window, text="Note:", bg='#917FB3', font=("Calibri", 16 * -1))
        note_window_note_label.place(x=30, y=150)
        # note_text = tk.Text(note_window, height=12, width=40,bd=3)
        # note_text.place(x=30,y=190)
        note_text_area = scrolledtext.ScrolledText(note_window, wrap=tk.WORD, bd=3, bg='#E5BEEC', width=40,
                                                   height=8, font=("Calibri", 16 * -1))

        note_text_area.grid(column=0, row=2, pady=190, padx=30)

        # note confirm button
        def note_window_confirm():
            ref = self.firebase_manager.get_notes_reference()
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H:%M")
            temp_data = {noted_id: {
                dt_string: {
                    'subject': note_window_subject_entry.get(),
                    'reporter': combo_reporter.get(),
                    'note': note_text_area.get("1.0", END).strip()
                }
            }}

            try:
                for key, value in temp_data.items():
                    ref.child(key).update(value)
                students.student_report_note(noted_id)
                messagebox.showinfo("Add Note Message", "Submitted successfully.", parent=note_window)
                note_window.destroy()
            except ValueError:
                messagebox.showerror("Add Note Error", "Failed to submit.", parent=note_window)

        # note confirm button
        note_confirm_btn = Button(note_window, text='Confirm', bd='5', fg="#FFFFFF", bg='#812e91',
                                  font=("Calibri", 16 * -1), activebackground='#917FB3', height='1', width='14',
                                  disabledforeground='gray', command=note_window_confirm)
        note_confirm_btn.place(x=30, y=400)

        # note cancel button
        def note_window_cancel():
            res = messagebox.askquestion('Cancel Note', 'Input will be lost, continue?', parent=note_window)
            if res == 'yes':
                note_window.destroy()

        note_cancel_btn = Button(note_window, text='Cancel', bd='5', fg="#FFFFFF", bg='#812e91',
                                 font=("Calibri", 16 * -1), activebackground='#917FB3', height='1', width='14',
                                 disabledforeground='gray', command=note_window_cancel)
        note_cancel_btn.place(x=180, y=400)

    # View Notes Window
    def view_note_popup(self, parent, noted_id):
        if len(noted_id) == 0:
            return
        view_note_window = Toplevel(parent)
        view_note_window.geometry("500x500+350+100")
        view_note_window.resizable(False, False)
        view_note_window.title("View Notes")
        view_note_window.configure(bg='#917FB3')

        view_note_window_label = Label(view_note_window, text="Select Date:",
                                       bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_label.place(x=30, y=30)

        view_note_window_id = Label(view_note_window, text="Student ID:",
                                    bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_id.place(x=30, y=70)
        view_note_window_id2 = Label(view_note_window, text=noted_id, bg='#917FB3', font=("Calibri", 16 * -1),
                                     borderwidth=1, relief="groove")
        view_note_window_id2.place(x=120, y=70)

        view_note_window_reporter = Label(view_note_window, text="Reporter:",
                                          bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_reporter.place(x=30, y=110)
        view_note_window_reporter2 = Label(view_note_window, text="(Reporter)",
                                           bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_reporter2.place(x=120, y=110)

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        view_note_window_date_label = Label(view_note_window, text=d1, bg='#917FB3', font=("Calibri", 16 * -1),
                                            borderwidth=3, relief="ridge")
        view_note_window_date_label.place(x=400, y=5)

        view_note_window_subject = Label(view_note_window, text="Subject:",
                                         bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_subject.place(x=30, y=150)
        view_note_window_subject2 = Label(view_note_window, text="(Subject)",
                                          bg='#917FB3', font=("Calibri", 16 * -1))
        view_note_window_subject2.place(x=120, y=150)

        view_note_text_area = scrolledtext.ScrolledText(view_note_window, wrap=tk.WORD, bd=3, background="#b6a4ba",
                                                        width=50, height=8, font=("Calibri", 16 * -1))

        view_note_text_area.grid(column=0, row=2, pady=190, padx=30)
        view_note_text_area.insert(INSERT, "(Select date to view)")
        view_note_text_area["state"] = "disabled"
        view_note_window.update()

        view_note_done_btn = Button(view_note_window, text='Done', bd='5', fg="#FFFFFF", bg='#812e91'
                                    , font=("Calibri", 16 * -1), activebackground='#917FB3', height='1',
                                    width='14', disabledforeground='gray', command=view_note_window.destroy)
        view_note_done_btn.place(x=350, y=400)

        ref = self.firebase_manager.get_student_notes(noted_id)
        res_dict = ref.order_by_key().get()
        if res_dict:
            res_keys = list(res_dict.keys())

        # Combobox functionality

        def combo_changed(event):
            selected_date = combo_dates.get()
            view_note_window_reporter2.configure(text=res_dict[selected_date]['reporter'])
            view_note_window_subject2.configure(text=res_dict[selected_date]['subject'])
            view_note_text_area.configure(state='normal')
            view_note_text_area.delete("1.0", "end")
            view_note_text_area.insert(INSERT, res_dict[selected_date]['note'])
            view_note_text_area.configure(state='disabled')

        # creating combo box
        combo_dates = ttk.Combobox(view_note_window, state="readonly", values=res_keys,
                                   background="gray", font=("Calibri", 16 * -1))
        combo_dates.place(x=120, y=35)

        combo_dates.bind("<<ComboboxSelected>>", combo_changed)
